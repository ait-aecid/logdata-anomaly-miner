from cerberus import Validator
from cerberus import TypeDefinition


class ParserModelType:
    """Defines a type for parser classes."""

    name = None
    is_model = False
    func = None

    def __init__(self, name):
        self.name = name
        if name.endswith('ModelElement'):
            self.is_model = True
            self.func = getattr(__import__("aminer.parsing." + name, fromlist=[name]), name)
        else:
            self.is_model = False
            # we need this import:
            # skipcq: PTC-W0034
            self.func = getattr(__import__(name), 'get_model')

    def __str__(self):
        return self.name


class AnalysisType:
    """Defines a type for analysis classes."""

    name = None
    func = None

    def __init__(self, name):
        self.name = name
        module = "aminer.analysis"
        if name in ('MatchPathFilter', 'MatchValueFilter', 'SubhandlerFilter'):
            module += '.AtomFilters'
        elif name in ('LinearNumericBinDefinition', 'ModuloTimeBinDefinition', 'PathDependentHistogramAnalysis', 'BinDefinition',
                      'HistogramData'):
            module += '.HistogramAnalysis'
        elif name in ('AndMatchRule', 'OrMatchRule', 'AtomFilterMatchAction', 'DebugHistoryMatchRule', 'EventGenerationMatchAction',
                      'DebugMatchRule', 'IPv4InRFC1918MatchRule', 'ModuloTimeMatchRule', 'NegationMatchRule', 'ParallelMatchRule',
                      'PathExistsMatchRule', 'StringRegexMatchRule', 'ValueDependentDelegatedMatchRule',
                      'ValueDependentModuloTimeMatchRule', 'ValueListMatchRule', 'ValueMatchRule', 'ValueRangeMatchRule'):
            module += '.Rules'
        elif name in ('TimeCorrelationDetector', 'CorrelationFeature'):
            module += '.TimeCorrelationDetector'
        elif name in ('TimeCorrelationViolationDetector', 'CorrelationRule', 'EventClassSelector'):
            module += '.TimeCorrelationViolationDetector'
        elif name == 'SimpleMonotonicTimestampAdjust':
            module += '.TimestampCorrectionFilters'
        else:
            module += '.' + name
        self.func = getattr(__import__(module, fromlist=[name]), name)

    def __str__(self):
        return self.name


class EventHandlerType:
    """Defines a type for event classes."""

    name = None
    func = None

    def __init__(self, name):
        self.name = name
        module = "aminer.events"
        if name in ('EventHandlerInterface', 'EventSourceInterface'):
            module += '.EventInterfaces'
        elif name == 'VolatileLogarithmicBackoffEventHistory':
            module += '.Utils'
        else:
            module += '.' + name
        self.func = getattr(__import__(module, fromlist=[name]), name)

    def __str__(self):
        return self.name


parser_type = TypeDefinition('parsermodel', (ParserModelType, str), ())
analysis_type = TypeDefinition('analysistype', (AnalysisType, str), ())
event_handler_type = TypeDefinition('eventhandlertype', (EventHandlerType, str), ())


class ConfigValidator(Validator):
    """Validates values from the configs."""

    types_mapping = Validator.types_mapping.copy()
    types_mapping['parsermodel'] = parser_type
    types_mapping['analysistype'] = analysis_type
    types_mapping['eventhandlertype'] = event_handler_type

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

    def _validate_has_start(self, has_start, field, value):
        """
        Test if there is a key named 'has_start'.
        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        seen_start = False
        for var in value:
            if "start" in var and var['start'] is True:
                if seen_start:
                    self._error(field, "Only one parser with 'start'-key is allowed")
                seen_start = True
        if has_start and not seen_start:
            self._error(field, "Parser must contain a 'start'-key")
