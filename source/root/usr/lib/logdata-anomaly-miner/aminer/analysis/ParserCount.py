"""This component counts occurring combinations of values and periodically sends the results as a report."""

import datetime
import time
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import TimeTriggeredComponentInterface


class ParserCount(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class creates a counter for path value combinations."""

    def __init__(self, aminer_config, target_path_list, report_event_handlers, report_interval=60, reset_after_report_flag=True):
        """Initialize the ParserCount component.
        @param aminer"""
        self.aminer_config = aminer_config
        self.target_path_list = target_path_list
        self.report_interval = report_interval
        self.report_event_handlers = report_event_handlers
        self.reset_after_report_flag = reset_after_report_flag
        self.count_dict = {}
        self.next_report_time = None
        if self.target_path_list is None:
            self.target_path_list = []

        for target_path in self.target_path_list:
            self.count_dict[target_path] = 0

    def get_time_trigger_class(self):
        """Get the trigger class this component can be registered for. This detector only needs persisteny triggers in real time."""
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def receive_atom(self, log_atom):
        match_dict = log_atom.parser_match.get_match_dictionary()
        for target_path in self.target_path_list:
            match_element = match_dict.get(target_path, None)
            if match_element is not None:
                self.count_dict[target_path] += 1
        if not self.target_path_list:
            shortest = 1000
            for key in match_dict:
                if match_dict[key].path.count('/') < shortest:
                    shortest = match_dict[key].path.count('/')
            for key in match_dict:
                if match_dict[key].path.count('/') == shortest:
                    if match_dict[key].path not in self.count_dict:
                        self.count_dict[match_dict[key].path] = 0
                    self.count_dict[match_dict[key].path] += 1

        if self.next_report_time is None:
            self.next_report_time = time.time() + self.report_interval
        return True

    def do_timer(self, trigger_time):
        """Check current ruleset should be persisted"""
        if self.next_report_time is None:
            return self.report_interval
        delta = self.next_report_time - trigger_time
        if delta <= 0:
            self.send_report()
            delta = 600
        return delta

    # skipcq: PYL-R0201
    def do_persist(self):
        """Immediately write persistence data to storage."""
        return False

    def send_report(self):
        """Sends a report to the event handlers."""
        output_string = 'Parsed paths in the last ' + str(self.report_interval) + ' seconds:\n'

        for k in self.count_dict:
            c = self.count_dict[k]
            output_string += '\t' + str(k) + ': ' + str(c) + '\n'

        event_data = {'StatusInfo': self.count_dict, 'FromTime': datetime.datetime.utcnow().timestamp() - self.report_interval,
                      'ToTime': datetime.datetime.utcnow().timestamp()}
        for listener in self.report_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Count report', [output_string], event_data, None, self)

        if self.reset_after_report_flag:
            for targetPath in self.target_path_list:
                self.count_dict[targetPath] = 0
