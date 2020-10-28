"""This component counts occurring combinations of values and periodically sends the results as a report.

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
from aminer import AMinerConfig
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
        self.log_total += 1
        match_dict = log_atom.parser_match.get_match_dictionary()
        success_flag = False
        for target_path in self.target_path_list:
            match_element = match_dict.get(target_path, None)
            if match_element is not None:
                self.count_dict[target_path] += 1
                success_flag = True
        if not self.target_path_list:
            path = iter(match_dict).__next__()
            if path not in self.count_dict:
                self.count_dict[path] = 0
            self.count_dict[path] += 1

        if self.next_report_time is None:
            self.next_report_time = time.time() + self.report_interval
        if success_flag:
            self.log_success += 1
        return True

    def do_timer(self, trigger_time):
        """Check current ruleset should be persisted"""
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
        """Sends a report to the event handlers."""
        output_string = 'Parsed paths in the last ' + str(self.report_interval) + ' seconds:\n'

        for k in self.count_dict:
            c = self.count_dict[k]
            output_string += '\t' + str(k) + ': ' + str(c) + '\n'
        output_string = output_string[:-1]

        event_data = {'StatusInfo': self.count_dict, 'FromTime': datetime.datetime.utcnow().timestamp() - self.report_interval,
                      'ToTime': datetime.datetime.utcnow().timestamp()}
        for listener in self.report_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Count report', [output_string], event_data, None, self)

        if self.reset_after_report_flag:
            for targetPath in self.target_path_list:
                self.count_dict[targetPath] = 0
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).debug('%s sent report.' % self.__class__.__name__)
