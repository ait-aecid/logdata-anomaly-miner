"""
This module defines a detector for time correlation between atoms.

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

from datetime import datetime
import random
import logging

from aminer.AminerConfig import DEBUG_LOG_NAME
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.analysis import Rules
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.History import get_log_int


class TimeCorrelationDetector(AtomHandlerInterface):
    """
    This class tries to find time correlation patterns between different log atoms.
    When a possible correlation rule is detected, it creates an event including the rules. This is useful to implement checks as depicted
    in http://dx.doi.org/10.1016/j.cose.2014.09.006.
    """

    time_trigger_class = AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def __init__(self, aminer_config, anomaly_event_handlers, parallel_check_count, persistence_id="Default",
                 record_count_before_event=10000, output_logline=True, use_path_match=True, use_value_match=True,
                 min_rule_attributes=1, max_rule_attributes=5):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param parallel_check_count number of rule detection checks to run in parallel.
        @param persistence_id name of persistence file.
        @param record_count_before_event number of events used to calculate statistics (i.e., window size)
        @param output_logline specifies whether the full parsed log atom should be provided in the output.
        @param min_rule_attributes minimum number of attributes forming a rule
        @param max_rule_attributes maximum number of attributes forming a rule
        @param use_path_match if true rules are build based on path existence
        @param use_value_match if true rules are built based on actual values
        """
        self.next_persist_time, self.log_success, self.log_total = [None]*3
        super().__init__(
            aminer_config=aminer_config, anomaly_event_handlers=anomaly_event_handlers, parallel_check_count=parallel_check_count,
            persistence_id=persistence_id, record_count_before_event=record_count_before_event, output_logline=output_logline,
            use_path_match=use_path_match, use_value_match=use_value_match, min_rule_attributes=min_rule_attributes,
            max_rule_attributes=max_rule_attributes
        )
        self.last_timestamp = 0.0
        self.last_unhandled_match = None
        self.total_records = 0

        if min_rule_attributes <= 0 or min_rule_attributes > max_rule_attributes:
            msg = "min_rule_attributes must not be smaller than max_rule_attributes and bigger than or equal to zero."
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise ValueError(msg)

        self.feature_list = []
        self.event_count_table = [0] * parallel_check_count * parallel_check_count * 2
        self.event_delta_table = [0] * parallel_check_count * parallel_check_count * 2

    def receive_atom(self, log_atom):
        """Receive a log atom from a source."""
        self.log_total += 1
        event_data = {}
        timestamp = log_atom.get_timestamp()
        if timestamp < self.last_timestamp:
            for listener in self.anomaly_event_handlers:
                listener.receive_event(
                    f"Analysis.{self.__class__.__name__}", f"Logdata not sorted: last {self.last_timestamp}, current {timestamp}",
                    [log_atom.parser_match.match_element.annotate_match("")], event_data, log_atom, self)
            return False
        self.last_timestamp = timestamp

        self.total_records += 1
        features_found_list = []

        for feature in self.feature_list:
            if feature.rule.match(log_atom):
                feature.trigger_count += 1
                self.update_tables_for_feature(feature, timestamp)
                features_found_list.append(feature)

        if len(self.feature_list) < self.parallel_check_count:
            if (random.randint(0, 1) != 0) and (self.last_unhandled_match is not None):
                log_atom = self.last_unhandled_match
            new_rule = self.create_random_rule(log_atom)
            if new_rule is not None:
                new_feature = CorrelationFeature(new_rule, len(self.feature_list), timestamp)
                self.feature_list.append(new_feature)
                new_feature.trigger_count = 1
                self.update_tables_for_feature(new_feature, timestamp)
                features_found_list.append(new_feature)

        for feature in features_found_list:
            feature.last_trigger_time = timestamp

        if not features_found_list:
            self.last_unhandled_match = log_atom

        if (self.total_records % self.record_count_before_event) == 0:
            result = self.total_records * [""]
            result[0] = self.analysis_status_to_string()
            value = log_atom.raw_data
            if isinstance(value, bytes):
                value = value.decode(AminerConfig.ENCODING)
            analysis_component = {"AffectedLogAtomPaths": list(log_atom.parser_match.get_match_dictionary()),
                                  "AffectedLogAtomValues": [value]}
            if self.output_logline:
                feature_list = []
                for feature in self.feature_list:
                    tmp_list = {}
                    r = self.rule_to_dict(feature.rule)
                    tmp_list["Rule"] = r
                    tmp_list["Index"] = feature.index
                    tmp_list["CreationTime"] = feature.creation_time
                    tmp_list["LastTriggerTime"] = feature.last_trigger_time
                    tmp_list["TriggerCount"] = feature.trigger_count
                    feature_list.append(tmp_list)
                analysis_component["FeatureList"] = feature_list
            analysis_component["AnalysisStatus"] = result[0]
            analysis_component["TotalRecords"] = self.total_records

            event_data["AnalysisComponent"] = analysis_component
            for listener in self.anomaly_event_handlers:
                listener.receive_event(f"Analysis.{self.__class__.__name__}", "Correlation report", result, event_data, log_atom, self)
            self.reset_statistics()
            logging.getLogger(DEBUG_LOG_NAME).debug("%s ran analysis.", self.__class__.__name__)
        self.log_success += 1
        return True

    def rule_to_dict(self, rule):
        """Convert a rule to a dict structure."""
        r = {"type": str(rule.__class__.__name__)}
        for var in vars(rule):
            attr = getattr(rule, var, None)
            if attr is None:
                r[var] = None
            elif isinstance(attr, list):
                tmp_list = []
                for v in attr:
                    d = self.rule_to_dict(v)
                    d["type"] = str(v.__class__.__name__)
                    tmp_list.append(d)
                r["subRules"] = tmp_list
            else:
                r[var] = attr
        return r

    def create_random_rule(self, log_atom):
        """Create a random existing path rule or value match rule."""
        parser_match = log_atom.parser_match
        sub_rules = []
        all_keys = list(parser_match.get_match_dictionary().keys())
        attribute_count = self.min_rule_attributes + get_log_int(self.max_rule_attributes - self.min_rule_attributes)

        while attribute_count > 0:
            key_pos = random.randint(0, len(all_keys) - 1)
            key_name = all_keys[key_pos]
            all_keys = all_keys[:key_pos] + all_keys[key_pos + 1:]
            key_value = parser_match.get_match_dictionary().get(key_name).match_object
            # Not much sense handling parsed date values in this implementation, so just ignore this attribute.
            if (isinstance(key_value, tuple)) and (isinstance(key_value[0], datetime)):
                if not all_keys:
                    break
                continue

            attribute_count -= 1
            rule_type = 1  # default is value_match only
            if self.use_path_match and self.use_value_match:
                rule_type = random.randint(0, 1)
            elif self.use_path_match:
                rule_type = 0
            if rule_type == 0:
                sub_rules.append(Rules.PathExistsMatchRule(key_name))
            else:
                sub_rules.append(Rules.ValueMatchRule(key_name, key_value))
            if not all_keys:
                break

        if len(sub_rules) > 1:
            return Rules.AndMatchRule(sub_rules)
        if len(sub_rules) > 0:
            return sub_rules[0]
        return None

    def update_tables_for_feature(self, target_feature, timestamp):
        """
        Assume that this event was the effect of a previous cause-related event.
        Loop over all cause-related features (rows) to search for matches.
        """
        feature_table_pos = (target_feature.index << 1)
        for feature in self.feature_list:
            delta = timestamp - feature.last_trigger_time
            if delta <= 10.0:
                self.event_count_table[feature_table_pos] += 1
                self.event_delta_table[feature_table_pos] += int(delta * 1000)
            feature_table_pos += (self.parallel_check_count << 1)

        feature_table_pos = ((target_feature.index * self.parallel_check_count) << 1) + 1
        for feature in self.feature_list:
            delta = timestamp - feature.last_trigger_time
            if delta <= 10.0:
                self.event_count_table[feature_table_pos] += 1
                self.event_delta_table[feature_table_pos] -= int(delta * 1000)
            feature_table_pos += 2

    def analysis_status_to_string(self):
        """Get a string representation of all features."""
        result = ""
        for feature in self.feature_list:
            trigger_count = feature.trigger_count
            result += f"{feature.rule} ({feature.index}) e = {trigger_count}:"
            stat_pos = (self.parallel_check_count * feature.index) << 1
            for feature_pos in range(len(self.feature_list)):  # skipcq: PTC-W0060
                event_count = self.event_count_table[stat_pos]
                ratio = "-"
                if trigger_count != 0:
                    # skipcq: PYL-C0209
                    ratio = "%.2e" % (float(event_count) / trigger_count)
                delta = "-"
                if event_count != 0:
                    # skipcq: PYL-C0209
                    delta = "%.2e" % (float(self.event_delta_table[stat_pos]) * 0.001 / event_count)
                # skipcq: PYL-C0209
                result += "\n  %d: {c = %#6d r = %s dt = %s" % (feature_pos, event_count, ratio, delta)
                stat_pos += 1
                event_count = self.event_count_table[stat_pos]
                ratio = "-"
                if trigger_count != 0:
                    # skipcq: PYL-C0209
                    ratio = "%.2e" % (float(event_count) / trigger_count)
                delta = "-"
                if event_count != 0:
                    # skipcq: PYL-C0209
                    delta = "%.2e" % (float(self.event_delta_table[stat_pos]) * 0.001 / event_count)
                # skipcq: PYL-C0209
                result += " c = %#6d r = %s dt = %s}" % (event_count, ratio, delta)
                stat_pos += 1
            result += "\n"
        return result

    def reset_statistics(self):
        """Reset all features."""
        for feature in self.feature_list:
            feature.creation_time = 0
            feature.last_trigger_time = 0
            feature.trigger_count = 0
        self.event_count_table = [0] * self.parallel_check_count * self.parallel_check_count * 2
        self.event_delta_table = [0] * self.parallel_check_count * self.parallel_check_count * 2


class CorrelationFeature:
    """This class defines a correlation feature."""

    def __init__(self, rule, index, creation_time):
        self.rule = rule
        self.index = index
        self.creation_time = creation_time
        self.last_trigger_time = 0.0
        self.trigger_count = 0
