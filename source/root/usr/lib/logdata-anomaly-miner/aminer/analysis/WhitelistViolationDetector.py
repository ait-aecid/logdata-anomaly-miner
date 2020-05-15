"""This module defines a detector for log atoms not matching
any whitelisted rule."""

import os

from aminer.input import AtomHandlerInterface
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX
from datetime import datetime


class WhitelistViolationDetector(AtomHandlerInterface):
    """Objects of this class handle a list of whitelist rules to ensure, that each received log-atom is at least covered by a
    single whitelist rule. To avoid traversing the complete rule tree more than once, the whitelist rules may have match actions
    attached that set off an alarm by themselves."""

    def __init__(self, aminer_config, whitelist_rules, anomaly_event_handlers, output_log_line=True):
        """Initialize the detector.
        @param whitelist_rules list of rules executed in same way as inside Rules.OrMatchRule."""
        self.whitelist_rules = whitelist_rules
        self.anomaly_event_handlers = anomaly_event_handlers
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.persistence_id = None

    def receive_atom(self, log_atom):
        """Receive on parsed atom and the information about the parser match.
        @param log_atom atom with parsed data to check
        @return True when logAtom is whitelisted, False otherwise."""
        event_data = {}
        for rule in self.whitelist_rules:
            if rule.match(log_atom):
                return True
        analysis_component = {'AffectedLogAtomPathes': list(log_atom.parser_match.get_match_dictionary()),
                              'AffectedLogAtomValues': [log_atom.raw_data.decode()]}
        original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX)
        if original_log_line_prefix is None:
            original_log_line_prefix = ''
        if self.output_log_line:
            match_paths_values = {}
            for match_path, match_element in log_atom.parser_match.get_match_dictionary().items():
                match_value = match_element.match_object
                if isinstance(match_value, tuple):
                    tmp_list = []
                    for val in match_value:
                        if isinstance(val, datetime):
                            tmp_list.append(datetime.timestamp(val))
                        else:
                            tmp_list.append(val)
                    match_value = tmp_list
                if isinstance(match_value, bytes):
                    match_value = match_value.decode()
                match_paths_values[match_path] = match_value
            analysis_component['ParsedLogAtom'] = match_paths_values
            sorted_log_lines = [
                log_atom.parser_match.match_element.annotate_match('') + os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
        else:
            sorted_log_lines = [original_log_line_prefix + repr(log_atom.raw_data)]
        event_data['AnalysisComponent'] = analysis_component
        for listener in self.anomaly_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, 'No whitelisting for current atom', sorted_log_lines,
                                   event_data, log_atom, self)
        return False
