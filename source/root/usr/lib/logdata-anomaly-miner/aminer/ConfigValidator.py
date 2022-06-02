from cerberus import Validator
from cerberus import TypeDefinition


class ParserModelType:
    """Defines a type for parser classes."""

    name = None
    is_model = False
    func = None

    def __init__(self, name):
        self.name = name
        if name.endswith("ModelElement"):
            self.is_model = True
            # Classes must be imported from the right modules. Some class names do not match the module name and need to be set explicitly.
            module = "aminer.parsing"
            if name == "DebugMatchContext":
                module += ".MatchContext"
            if name == "MultiLocaleDateTimeModelElement":
                module += ".DateTimeModelElement"
            else:
                module += "." + name
            self.func = getattr(__import__(module, fromlist=[name]), name)
        else:
            self.is_model = False
            try:
                self.func = __import__(name).get_model
            except (AttributeError, ImportError) as e:
                ymlext = ['.yml', '.YAML', '.YML', '.yaml']
                module = None
                for path in sys.path:
                    for extension in ymlext:
                        abs_path = os.path.join(path, name + extension)
                        if os.path.exists(abs_path):
                            module = abs_path
                            break
                if module is not None:
                    import yaml
                    import copy
                    from aminer.AminerConfig import DEBUG_LOG_NAME
                    from aminer.YamlConfig import filter_config_errors, build_parsing_model
                    with open(module) as yamlfile:  # skipcq: PTC-W6004
                        try:
                            yaml_data = yaml.safe_load(yamlfile)
                        except yaml.YAMLError as exception:
                            logging.getLogger(DEBUG_LOG_NAME).error(exception)
                            raise exception

                    with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schemas/normalisation/ParserNormalisationSchema.yml',
                              'r') as sma:
                        # skipcq: PYL-W0123
                        parser_normalisation_schema = eval(sma.read())
                    with open(os.path.dirname(os.path.abspath(__file__)) + '/' + 'schemas/validation/ParserValidationSchema.yml',
                              'r') as sma:
                        # skipcq: PYL-W0123
                        parser_validation_schema = eval(sma.read())
                    normalisation_schema = {**parser_normalisation_schema}
                    validation_schema = {**parser_validation_schema}

                    v = ConfigValidator(validation_schema)
                    if not v.validate(yaml_data, validation_schema):
                        filtered_errors = copy.deepcopy(v.errors)
                        filter_config_errors(filtered_errors, 'Parser', v.errors, parser_validation_schema)
                    v = NormalisationValidator(normalisation_schema)
                    if v.validate(yaml_data, normalisation_schema):
                        test = v.normalized(yaml_data)
                        yaml_data = test
                    else:
                        logging.getLogger(DEBUG_LOG_NAME).error(v.errors)
                        raise ValueError(v.errors)
                    self.func = build_parsing_model(yaml_data)
                    if callable(self.func):
                        self.func = self.func()
                else:
                    raise e

    def __str__(self):
        return self.name


class AnalysisType:
    """Defines a type for analysis classes."""

    name = None
    func = None

    def __init__(self, name):
        self.name = name
        # Classes must be imported from the right modules. Some class names do not match the module name and need to be set explicitly.
        module = "aminer.analysis"
        if name in ("MatchPathFilter", "MatchValueFilter", "SubhandlerFilter"):
            module += ".AtomFilters"
        elif name in ("LinearNumericBinDefinition", "ModuloTimeBinDefinition", "PathDependentHistogramAnalysis", "BinDefinition",
                      "HistogramData"):
            module += ".HistogramAnalysis"
        elif name in ("AndMatchRule", "OrMatchRule", "AtomFilterMatchAction", "DebugHistoryMatchRule", "EventGenerationMatchAction",
                      "DebugMatchRule", "IPv4InRFC1918MatchRule", "ModuloTimeMatchRule", "NegationMatchRule", "ParallelMatchRule",
                      "PathExistsMatchRule", "StringRegexMatchRule", "ValueDependentDelegatedMatchRule",
                      "ValueDependentModuloTimeMatchRule", "ValueListMatchRule", "ValueMatchRule", "ValueRangeMatchRule"):
            module += ".Rules"
        elif name in ("TimeCorrelationDetector", "CorrelationFeature"):
            module += ".TimeCorrelationDetector"
        elif name in ("TimeCorrelationViolationDetector", "CorrelationRule", "EventClassSelector"):
            module += ".TimeCorrelationViolationDetector"
        elif name == "SimpleMonotonicTimestampAdjust":
            module += ".TimestampCorrectionFilters"
        elif name in ("SimpleUnparsedAtomHandler", "VerboseUnparsedAtomHandler"):
            module += ".UnparsedAtomHandlers"
        else:
            module += "." + name
        self.func = getattr(__import__(module, fromlist=[name]), name)

    def __str__(self):
        return self.name


class EventHandlerType:
    """Defines a type for event classes."""

    name = None
    func = None

    def __init__(self, name):
        self.name = name
        # Classes must be imported from the right modules. Some class names do not match the module name and need to be set explicitly.
        module = "aminer.events"
        if name in ("EventHandlerInterface", "EventSourceInterface"):
            module += ".EventInterfaces"
        elif name == "VolatileLogarithmicBackoffEventHistory":
            module += ".Utils"
        else:
            module += "." + name
        self.func = getattr(__import__(module, fromlist=[name]), name)

    def __str__(self):
        return self.name


parser_type = TypeDefinition("parsermodel", (ParserModelType, str), ())
analysis_type = TypeDefinition("analysistype", (AnalysisType, str), ())
event_handler_type = TypeDefinition("eventhandlertype", (EventHandlerType, str), ())


class ConfigValidator(Validator):
    """Validates values from the configs."""

    def _validate_has_start(self, has_start, field, value):
        """
        Test if there is a key named "has_start".
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        seen_start = False
        for var in value:
            if "start" in var and var["start"] is True:
                if seen_start:
                    self._error(field, 'Only one parser with "start"-key is allowed')
                seen_start = True
        if has_start and not seen_start:
            self._error(field, 'Parser must contain a "start"-key')

    def _validate_bigger_than_or_equal(self, bigger_than_or_equal, field, value):
        """
        Check if the value of the current attribute is bigger than the value of bigger_than.
        This check works for integers and floats.
        Usage:
        {"bigger_than_or_equal": ["lower_value_attribute", default_value_if_not_defined]}
        For example:
        "max_num_vals": {"type": "integer", "bigger_than_or_equal": ["min_num_vals", 1000]}

        The rule's arguments are validated against this schema:
        {'type': 'list'}
        """
        key, default_value = bigger_than_or_equal
        if key not in self.document:
            lower_value = default_value
        else:
            lower_value = self.document[key]
        if value < lower_value:
            self._error(field, "%s(=%s) must be bigger than or equal with %s(=%s)." % (field, str(value), key, str(self.document[key])))


class NormalisationValidator(ConfigValidator):
    """Normalises values from the configs."""

    types_mapping = Validator.types_mapping.copy()
    types_mapping["parsermodel"] = parser_type
    types_mapping["analysistype"] = analysis_type
    types_mapping["eventhandlertype"] = event_handler_type

    # we skip the following issue, otherwise an
    # "must have self"-issue will pop up
    # skipcq: PYL-R0201
    def _normalize_coerce_toparsermodel(self, value):
        """Create a ParserModelType from the string representation."""
        if isinstance(value, str):
            return ParserModelType(value)
        return None

    # we skip the following issue, otherwise an
    # "must have self"-issue will pop up
    # skipcq: PYL-R0201
    def _normalize_coerce_toanalysistype(self, value):
        """Create a AnalysisType from the string representation."""
        if isinstance(value, str):
            return AnalysisType(value)
        return None

    # we skip the following issue, otherwise an
    # "must have self"-issue will pop up
    # skipcq: PYL-R0201
    def _normalize_coerce_toeventhandlertype(self, value):
        """Create a EventHandlerType from the string representation."""
        if isinstance(value, str):
            return EventHandlerType(value)
        return None
