"""
This module defines a detector that reports diverges from an average.

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

import os
import logging

from aminer.AminerConfig import build_persistence_file_name, KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD, DEBUG_LOG_NAME
from aminer.AnalysisChild import AnalysisContext
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util import PersistenceUtil
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class MatchValueAverageChangeDetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """
    This detector calculates the average of a given list of values to monitor.
    Reports are generated if the average of the latest diverges significantly from the values observed before.
    """

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, timestamp_path, target_path_list, min_bin_elements, min_bin_time,
                 debug_mode=False, persistence_id="Default", output_logline=True, learn_mode=False, avg_factor=1, var_factor=2,
                 log_resource_ignore_list=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param timestamp_path if not None, use this path value for timestamp based bins.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that all values occurring in these paths are
               considered for value range generation.
        @param learn_mode specifies whether new statistics should be learned.
        @param min_bin_elements evaluate the latest bin only after at least that number of elements was added to it.
        @param min_bin_time evaluate the latest bin only when the first element is received after min_bin_time has elapsed.
        @param avg_factor the maximum allowed deviation for the average value before an anomaly is raised.
        @param var_factor the maximum allowed deviation for the variance of the value before an anomaly is raised.
        @param debug_mode if true, generate an analysis report even when average of last bin was within expected range.
        @param persistence_id name of persistence file.
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        """
        # avoid "defined outside init" issue
        self.next_persist_time, self.log_success, self.log_total = [None] * 3
        super().__init__(
            aminer_config=aminer_config, anomaly_event_handlers=anomaly_event_handlers, timestamp_path=timestamp_path,
            target_path_list=target_path_list, min_bin_elements=min_bin_elements, min_bin_time=min_bin_time, debug_mode=debug_mode,
            persistence_id=persistence_id, output_logline=output_logline, avg_factor=avg_factor, var_factor=var_factor,
            learn_mode=learn_mode, log_resource_ignore_list=log_resource_ignore_list, mutable_default_args=["log_resource_ignore_list"]
        )
        if not self.target_path_list:
            msg = "target_path_list must not be empty or None."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)

        self.persistence_file_name = build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)
        self.stat_data = []
        self.load_persistence_data()

    def receive_atom(self, log_atom):
        """Send summary to all event handlers."""
        for source in self.log_resource_ignore_list:
            if log_atom.source.resource_name == source:
                return
        self.log_total += 1
        parser_match = log_atom.parser_match
        value_dict = parser_match.get_match_dictionary()

        timestamp_value = log_atom.get_timestamp()
        if self.timestamp_path is not None:
            match_value = value_dict.get(self.timestamp_path)
            if match_value is None:
                return
            timestamp_value = match_value.match_object
            event_data = {"MatchValue": match_value.match_object}

        analysis_summary = ""
        ready_for_analysis_flag = True
        for (path, stat_data) in self.stat_data:
            match = value_dict.get(path)
            if match is None:
                ready_for_analysis_flag = (self.update(stat_data, timestamp_value, None) and ready_for_analysis_flag)
            else:
                if isinstance(match, list):
                    data = []
                    for m in match:
                        data.append(m.match_object)
                else:
                    data = match.match_object
                ready_for_analysis_flag = (self.update(stat_data, timestamp_value, data) and ready_for_analysis_flag)

        if ready_for_analysis_flag:
            anomaly_scores = []
            for (path, stat_data) in self.stat_data:
                analysis_data = self.analyze(stat_data)
                if analysis_data is not None:
                    d = {"Path": path}
                    a = {}
                    new = {"N": analysis_data[1], "Avg": analysis_data[2], "Var": analysis_data[3]}
                    old = {"N": analysis_data[4], "Avg": analysis_data[5], "Var": analysis_data[6]}
                    a["New"] = new
                    a["Old"] = old
                    d["AnalysisData"] = a
                    if analysis_summary == "":
                        analysis_summary += f'"{path}": {analysis_data[0]}'
                    else:
                        analysis_summary += os.linesep
                        analysis_summary += f'  "{path}": {analysis_data[0]}'
                    anomaly_scores.append(d)
            analysis_component = {"AffectedLogAtomPaths": list(value_dict),
                                  "AnomalyScores": anomaly_scores,
                                  "MinBinElements": self.min_bin_elements,
                                  "MinBinTime": self.min_bin_time,
                                  "DebugMode": self.debug_mode}
            event_data = {"AnalysisComponent": analysis_component}

        if analysis_summary:
            res = [""] * stat_data[2][0]
            res[0] = analysis_summary
            for listener in self.anomaly_event_handlers:
                listener.receive_event(f"Analysis.{self.__class__.__name__}", "Statistical data report", res, event_data, log_atom, self)
        self.log_success += 1

    def do_timer(self, trigger_time):
        """Check if current ruleset should be persisted."""
        if self.next_persist_time is None:
            return self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)

        delta = self.next_persist_time - trigger_time
        if delta <= 0:
            self.do_persist()
            delta = self.aminer_config.config_properties.get(KEY_PERSISTENCE_PERIOD, DEFAULT_PERSISTENCE_PERIOD)
            self.next_persist_time = trigger_time + delta
        return delta

    def load_persistence_data(self):
        """Load the persistence data from storage."""
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        for path in self.target_path_list:
            self.stat_data.append((path, [],))

        def replace_brackets(val):
            """replace lists with tuples."""
            if isinstance(val, list):
                val = tuple(val)
            return val

        if persistence_data is not None:
            for val in persistence_data:
                values = replace_brackets(val[1])
                index = 0
                for p, _ in self.stat_data:
                    if p == val[0]:
                        break
                    index += 1
                for value in values:
                    value = replace_brackets(value)
                    self.stat_data[index][1].append(value)

    def do_persist(self):
        """Immediately write persistence data to storage."""
        PersistenceUtil.store_json(self.persistence_file_name, self.stat_data)
        logging.getLogger(DEBUG_LOG_NAME).debug("%s persisted data.", self.__class__.__name__)

    def update(self, stat_data, timestamp_value, value):
        """
        Update the collected statistics data.
        @param value if value not None, check only conditions if current bin is full enough.
        @return true if the bin is full enough to perform an analysis.
        """
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
        """
        Perform the analysis and progress from the last bin to the next one.
        @return None when statistical data was as expected and debugging is disabled.
        """
        logging.getLogger(DEBUG_LOG_NAME).debug("%s performs analysis.", self.__class__.__name__)
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
                return [f"Initial: n = {current_bin[0]}, avg = {current_average + stat_data[1]}, var = {current_variance}"] + [None]*10
        else:
            total_n = old_bin[0] + current_bin[0]
            total_sum = old_bin[1] + current_bin[1]
            total_sum2 = old_bin[2] + current_bin[2]

            if self.learn_mode:
                stat_data[2] = (
                    total_n, total_sum, total_sum2, total_sum / total_n, (total_sum2 - (total_sum * total_sum) / total_n) / (total_n - 1))
            stat_data[3] = (0, 0.0, 0.0)

            if (current_variance > self.var_factor * old_bin[4]) or (abs(current_average - old_bin[3]) > self.avg_factor * old_bin[4]) or \
               self.debug_mode:
                res = [f"Change: new: n = {current_bin[0]}, avg = {current_average + stat_data[1]}, var = {current_variance}; old: n = "
                       f"{old_bin[0]}, avg = {old_bin[3] + stat_data[1]}, var = { old_bin[4]}", current_bin[0],
                       current_average + stat_data[1], current_variance, old_bin[0], old_bin[3] + stat_data[1], old_bin[4]]
                return res
        return None
