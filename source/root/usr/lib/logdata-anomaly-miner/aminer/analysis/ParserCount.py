"""
This component counts occurring combinations of values and periodically sends the results as a report.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

import datetime
import time
import logging
from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer.AnalysisChild import AnalysisContext
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


current_processed_lines_str = 'CurrentProcessedLines'
total_processed_lines_str = 'TotalProcessedLines'


class ParserCount(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class creates a counter for path value combinations."""

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, target_path_list, report_event_handlers, report_interval=60, target_label_list=None,
                 split_reports_flag=False):
        """Initialize the ParserCount component."""
        self.aminer_config = aminer_config
        self.target_path_list = target_path_list
        self.target_label_list = target_label_list
        self.report_interval = report_interval
        self.report_event_handlers = report_event_handlers
        self.split_reports_flag = split_reports_flag
        self.count_dict = {}
        self.next_report_time = None
        if (target_path_list is None or target_path_list == []) and (target_label_list is not None and target_label_list != []):
            msg = 'Target labels cannot be used without specifying target paths.'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if target_path_list is not None and target_label_list is not None and len(target_path_list) != len(target_label_list):
            msg = 'Every path must have a target label if target labels are used.'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)
        if self.target_path_list is None:
            self.target_path_list = []

        for target_path in self.target_path_list:
            if self.target_label_list:
                target_path = self.target_label_list[self.target_path_list.index(target_path)]
            self.count_dict[target_path] = {current_processed_lines_str: 0, total_processed_lines_str: 0}

    def receive_atom(self, log_atom):
        """Receive a log atom from a source."""
        self.log_total += 1
        match_dict = log_atom.parser_match.get_match_dictionary()
        success_flag = False
        for target_path in self.target_path_list:
            match_element = match_dict.get(target_path)
            if match_element is not None:
                success_flag = True
                if self.target_label_list:
                    target_path = self.target_label_list[self.target_path_list.index(target_path)]
                self.count_dict[target_path][current_processed_lines_str] += 1
                self.count_dict[target_path][total_processed_lines_str] += 1
        if not self.target_path_list:
            path = iter(match_dict).__next__()
            if path not in self.count_dict:
                self.count_dict[path] = {current_processed_lines_str: 0, total_processed_lines_str: 0}
            self.count_dict[path][current_processed_lines_str] += 1
            self.count_dict[path][total_processed_lines_str] += 1

        if self.next_report_time is None:
            self.next_report_time = time.time() + self.report_interval
        if success_flag:
            self.log_success += 1
        return True

    def do_timer(self, trigger_time):
        """Check current ruleset should be persisted."""
        if self.next_report_time is None:
            return self.report_interval
        delta = self.next_report_time - trigger_time
        if delta < 0:
            self.send_report()
            delta = self.report_interval
        return delta

    # skipcq: PYL-R0201
    def do_persist(self):
        """Immediately write persistence data to storage."""
        return False

    def send_report(self):
        """Send a report to the event handlers."""
        output_string = 'Parsed paths in the last ' + str(self.report_interval) + ' seconds:\n'
        if not self.split_reports_flag:
            for k in self.count_dict:
                c = self.count_dict[k]
                output_string += '\t' + str(k) + ': ' + str(c) + '\n'
            output_string = output_string[:-1]
            event_data = {'StatusInfo': self.count_dict, 'FromTime': datetime.datetime.utcnow().timestamp() - self.report_interval,
                          'ToTime': datetime.datetime.utcnow().timestamp()}
            for listener in self.report_event_handlers:
                listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Count report', [output_string], event_data, None, self)
        else:
            for k in self.count_dict:
                output_string = 'Parsed paths in the last ' + str(self.report_interval) + ' seconds:\n'
                c = self.count_dict[k]
                output_string += '\t' + str(k) + ': ' + str(c)
                status_info = {k: {
                    current_processed_lines_str: c[current_processed_lines_str],
                    total_processed_lines_str: c[total_processed_lines_str]}}
                event_data = {'StatusInfo': status_info, 'FromTime': datetime.datetime.utcnow().timestamp() - self.report_interval,
                              'ToTime': datetime.datetime.utcnow().timestamp()}
                for listener in self.report_event_handlers:
                    listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Count report', [output_string], event_data, None, self)
        for k in self.count_dict:
            self.count_dict[k][current_processed_lines_str] = 0
        logging.getLogger(DEBUG_LOG_NAME).debug('%s sent report.', self.__class__.__name__)
