from cerberus import Validator
from cerberus import TypeDefinition


class ParserModelType:
    name = None
    ismodel = False
    func = None

    def __init__(self, name):
        self.name = name
        if name.endswith('ModelElement'):
            self.ismodel = True
            self.func = getattr(__import__("aminer.parsing", fromlist=[name]), name)
        else:
            self.ismodel = False
            # we need this import:
            # skipcq: PTC-W0034
            self.func = getattr(__import__(name), 'get_model')

    def __str__(self):
        return self.name


class AnalysisType:
    name = None
    func = None

    def __init__(self, name):
        self.name = name
        self.func = getattr(__import__("aminer.analysis", fromlist=[name]), name)

    def __str__(self):
        return self.name


parser_type = TypeDefinition('parsermodel', (ParserModelType, str), ())
analysis_type = TypeDefinition('analysistype', (AnalysisType, str), ())


class ConfigValidator(Validator):
    types_mapping = Validator.types_mapping.copy()
    types_mapping['parsermodel'] = parser_type
    types_mapping['analysistype'] = analysis_type

    def _normalize_coerce_toparsermodel(self, value):
        if isinstance(value, str):
            return ParserModelType(value)
        return None

    def _normalize_coerce_toanalysistype(self, value):
        if isinstance(value, str):
            return AnalysisType(value)
        return None

    def _validate_has_start(self, has_start, field, value):
        """ Test if there is a key named 'has_start'.
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
