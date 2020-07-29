"""This module defines a filter for parsed paths and values."""

import os

from aminer.input import AtomHandlerInterface
from aminer.analysis import CONFIG_KEY_LOG_LINE_PREFIX

class MatchFilter(AtomHandlerInterface):
    """This class creates events for specified paths and values."""


    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers,
               target_value_list=None, output_log_line=True):
        """Initialize the detector."""
        self.target_path_list = target_path_list
        self.target_value_list = target_value_list
        self.anomaly_event_handlers = anomaly_event_handlers
        self.aminer_config = aminer_config
        self.output_log_line = output_log_line
        self.persistence_id = 'Not persisted'

    def receive_atom(self, log_atom):
        """Forward all log atoms that involve specified path and optionally value."""
        match_dict = log_atom.parser_match.get_match_dictionary()
        for target_path in self.target_path_list:
            match = match_dict.get(target_path, None)
            if match is None:
                continue
            event_data = {}
            if isinstance(match.match_object, bytes):
                affected_log_atom_values = match.match_object.decode()
            else:
                affected_log_atom_values = match.match_object
            if self.target_value_list is not None and affected_log_atom_values not in self.target_value_list:
                continue
            original_log_line_prefix = self.aminer_config.config_properties.get(CONFIG_KEY_LOG_LINE_PREFIX)
            if original_log_line_prefix is None:
                original_log_line_prefix = ''
            analysis_component = {'AffectedLogAtomPaths': [target_path], 'AffectedLogAtomValues': [str(affected_log_atom_values)]}
            if self.output_log_line:
                match_paths_values = {}
                for match_path, match_element in match_dict.items():
                    match_value = match_element.match_object
                    if isinstance(match_value, bytes):
                        match_value = match_value.decode()
                    match_paths_values[match_path] = match_value
                analysis_component['ParsedLogAtom'] = match_paths_values
                sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') +
                    os.linesep + original_log_line_prefix + repr(log_atom.raw_data)]
            else:
                sorted_log_lines = [original_log_line_prefix + repr(log_atom.raw_data)]
            event_data = {'AnalysisComponent': analysis_component}
            for listener in self.anomaly_event_handlers:
                listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Log Atom Filtered',
                                       sorted_log_lines, event_data, log_atom, self)
