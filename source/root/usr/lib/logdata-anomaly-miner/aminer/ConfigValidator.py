from cerberus import Validator

class ConfigValidator(Validator):
    def _validate_has_start(self, has_start, field, value):
        seen_start = False
        for var in value:
            if "start" in var and var['start'] is True:
                if seen_start:
                    self._error(field, "Only one parser with 'start'-key is allowed")
                seen_start = True
        if has_start and not seen_start:
            self._error(field, "Parser must contain a 'start'-key")
