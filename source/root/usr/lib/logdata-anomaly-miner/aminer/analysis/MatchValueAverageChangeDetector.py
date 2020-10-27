"""This module defines a detector that reports diverges from
an average.

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

import time
import os

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface


class MatchValueAverageChangeDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This detector calculates the average of a given list of values to monitor and reports if the average of the latest diverges
    significantly from the values observed before."""

    def __init__(self, aminer_config, anomaly_event_handlers, timestamp_path, analyze_path_list, min_bin_elements, min_bin_time,
                 sync_bins_flag=True, debug_mode=False, persistence_id='Default', output_log_line=True):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param timestamp_path if not None, use this path value for timestamp based bins.
        @param analyze_path_list list of match pathes to analyze in this detector.
        @param min_bin_elements evaluate the latest bin only after at least that number of elements was added to it.
        @param min_bin_time evaluate the latest bin only when the first element is received after minBinTime has elapsed.
        @param sync_bins_flag if true the bins of all analyzed path values have to be filled enough to trigger analysis.
        @param debug_mode if true, generate an analysis report even when average of last bin was within expected range."""
        self.anomaly_event_handlers = anomaly_event_handlers
        self.timestamp_path = timestamp_path
        self.min_bin_elements = min_bin_elements
        self.min_bin_time = min_bin_time
        self.sync_bins_flag = sync_bins_flag
        self.debug_mode = debug_mode
        self.next_persist_time = None
        self.persistence_id = persistence_id
        self.output_log_line = output_log_line

        PersistencyUtil.add_persistable_component(self)
        self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, 'MatchValueAverageChangeDetector',
                                                                              persistence_id)
        persistence_data = PersistencyUtil.load_json(self.persistence_file_name)
        if persistence_data is None:
            self.stat_data = []
            for path in analyze_path_list:
                self.stat_data.append((path, [],))

    def receive_atom(self, log_atom):
        """Sends summary to all event handlers."""
        parser_match = log_atom.parser_match
        value_dict = parser_match.get_match_dictionary()

        timestamp_value = log_atom.get_timestamp()
        if self.timestamp_path is not None:
            match_value = value_dict.get(self.timestamp_path)
            if match_value is None:
                return
            timestamp_value = match_value.match_object
            event_data = {'MatchValue': match_value.match_object}

        analysis_summary = ''
        if self.sync_bins_flag:
            ready_for_analysis_flag = True
            for (path, stat_data) in self.stat_data:
                match = value_dict.get(path, None)
                if match is None:
                    ready_for_analysis_flag = (ready_for_analysis_flag and self.update(stat_data, timestamp_value, None))
                else:
                    ready_for_analysis_flag = (ready_for_analysis_flag and self.update(stat_data, timestamp_value, match.match_object))

            if ready_for_analysis_flag:
                anomaly_scores = []
                for (path, stat_data) in self.stat_data:
                    analysis_data = self.analyze(stat_data)
                    if analysis_data is not None:
                        d = {'Path': path}
                        a = {}
                        new = {'N': analysis_data[1], 'Avg': analysis_data[2], 'Var': analysis_data[3]}
                        old = {'N': analysis_data[4], 'Avg': analysis_data[5], 'Var': analysis_data[6]}
                        a['New'] = new
                        a['Old'] = old
                        d['AnalysisData'] = a
                        if analysis_summary == '':
                            analysis_summary += '"%s": %s' % (path, analysis_data[0])
                        else:
                            analysis_summary += os.linesep
                            analysis_summary += '  "%s": %s' % (path, analysis_data[0])
                        anomaly_scores.append(d)
                analysis_component = {'AffectedLogAtomPathes': list(value_dict)}
                if self.output_log_line:
                    match_paths_values = {}
                    for match_path, match_element in log_atom.parser_match.get_match_dictionary().items():
                        match_value = match_element.match_object
                        if isinstance(match_value, bytes):
                            match_value = match_value.decode()
                        match_paths_values[match_path] = match_value
                    analysis_component['ParsedLogAtom'] = match_paths_values
                analysis_component['AnomalyScores'] = anomaly_scores
                analysis_component['MinBinElements'] = self.min_bin_elements
                analysis_component['MinBinTime'] = self.min_bin_time
                analysis_component['SyncBinsFlag'] = self.sync_bins_flag
                analysis_component['DebugMode'] = self.debug_mode
                event_data = {'AnalysisComponent': analysis_component}

                if self.next_persist_time is None:
                    self.next_persist_time = time.time() + 600
        else:
            raise Exception('FIXME: not implemented')

        if analysis_summary:
            res = [''] * stat_data[2][0]
            res[0] = analysis_summary
            for listener in self.anomaly_event_handlers:
                listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Statistical data report', res, event_data, log_atom, self)

    def get_time_trigger_class(self):
        """Get the trigger class this component should be registered for. This trigger is used only for persistency, so real-time
        triggering is needed."""
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check current ruleset should be persisted"""
        if self.next_persist_time is None:
            return 600

        delta = self.next_persist_time - trigger_time
        if delta < 0:
            self.next_persist_time = None
            delta = 600
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        self.next_persist_time = None

    def update(self, stat_data, timestamp_value, value):
        """Update the collected statistics data.
        @param value if value not None, check only conditions if current bin is full enough.
        @return true if the bin is full enough to perform an analysis."""

        if value is not None:
            if not stat_data:
                # Append timestamp, k-value, old-bin (n, sum, sum2, avg, variance),
                # current-bin (n, sum, sum2)
                stat_data.append(timestamp_value)
                stat_data.append(value)
                stat_data.append(None)
                stat_data.append((1, 0.0, 0.0,))
            else:
                delta = value - stat_data[1]
                bin_values = stat_data[3]
                stat_data[3] = (bin_values[0] + 1, bin_values[1] + delta, bin_values[2] + delta * delta)

        if not stat_data:
            return False
        if stat_data[3][0] < self.min_bin_elements:
            return False
        if self.timestamp_path is not None:
            return timestamp_value - stat_data[0] >= self.min_bin_time
        return True

    def analyze(self, stat_data):
        """Perform the analysis and progress from the last bin to the next one.
        @return None when statistical data was as expected and debugging is disabled."""

        current_bin = stat_data[3]
        current_average = current_bin[1] / current_bin[0]
        current_variance = (current_bin[2] - (current_bin[1] * current_bin[1]) / current_bin[0]) / (current_bin[0] - 1)
        # Append timestamp, k-value, old-bin (n, sum, sum2, avg, variance),
        # current-bin (n, sum, sum2)

        old_bin = stat_data[2]
        if old_bin is None:
            stat_data[2] = (current_bin[0], current_bin[1], current_bin[2], current_average, current_variance,)
            stat_data[3] = (0, 0.0, 0.0)
            if self.debug_mode:
                return 'Initial: n = %d, avg = %s, var = %s' % (current_bin[0], current_average + stat_data[1], current_variance)
        else:
            total_n = old_bin[0] + current_bin[0]
            total_sum = old_bin[1] + current_bin[1]
            total_sum2 = old_bin[2] + current_bin[2]

            stat_data[2] = (
                total_n, total_sum, total_sum2, total_sum / total_n, (total_sum2 - (total_sum * total_sum) / total_n) / (total_n - 1))
            stat_data[3] = (0, 0.0, 0.0)

            if (current_variance > 2 * old_bin[4]) or (abs(current_average - old_bin[3]) > old_bin[4]) or self.debug_mode:
                res = ['Change: new: n = %d, avg = %s, var = %s; old: n = %d, avg = %s, var = %s' % (
                    current_bin[0], current_average + stat_data[1], current_variance, old_bin[0], old_bin[3] + stat_data[1], old_bin[4]),
                    current_bin[0], current_average + stat_data[1], current_variance, old_bin[0], old_bin[3] + stat_data[1], old_bin[4]]
                return res
        return None
