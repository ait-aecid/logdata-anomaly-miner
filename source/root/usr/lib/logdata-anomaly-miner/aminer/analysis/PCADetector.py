"""
This module defines a PCA-detector for event and value counts.
The component detects anomalies by creating an Event-Count-Matrix for given
time-windows to calculate an anomaly score for new time windows afterwards by
using the reconstruction error from the inverse-transformation with restricted
components of the Principal-Component-Analysis (PCA).

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
import copy
import numpy as np
import logging
import os
from aminer import AminerConfig
from aminer.AminerConfig import STAT_LEVEL, STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX
from aminer.AnalysisChild import AnalysisContext
from aminer.util import PersistenceUtil
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface


class PCADetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class creates events if event or value occurrence counts are outliers in PCA space."""

    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, window_size, min_anomaly_score, min_variance, num_windows,
                 persistence_id='Default', auto_include_flag=False, output_log_line=True, ignore_list=None, constraint_list=None):
        """
        Initialize the detector. This will also trigger reading or creation of persistence storage location.
        @param aminer_config configuration from analysis_context.
        @param target_path_list parser paths of values to be analyzed. Multiple paths mean that values are analyzed as separate
        dimensions. When no paths are specified, the events given by the full path list are analyzed (one dimension).
        @param anomaly_event_handlers for handling events, e.g., print events to stdout.
        @param window_size the length of the time window for counting in seconds.
        @param min_anomaly_score the minimum computed outlier score for reporting anomalies. Scores are scaled by training data, i.e.,
        reasonable minimum scores are >1 to detect outliers with respect to currently trained PCA matrix.
        @param min_variance the minimum variance covered by the principal components in range [0, 1].
        @param num_windows the number of time windows in the sliding window approach. Total covered time span = window_size * num_windows.
        @param persistence_id name of persistency document.
        @param auto_include_flag specifies whether new count measurements are added to the PCA count matrix.
        @param output_log_line specifies whether the full parsed log atom should be provided in the output.
        @param ignore_list list of paths that are not considered for analysis, i.e., events that contain one of these paths are
        omitted. The default value is [] as None is not iterable.
        @param constrain_list list of paths that have to be present in the log atom to be analyzed.
        """
        self.target_path_list = target_path_list
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.next_persist_time = None
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.persistence_id = persistence_id
        self.block_time = window_size
        self.anomaly_score_threshold = min_anomaly_score
        self.variance_threshold = min_variance
        if num_windows < 3:
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).warning('num_windows must be >= 3!')
            self.num_windows = 3
        else:
            self.num_windows = num_windows
        self.first_log = True
        self.start_time = 0
        self.constraint_list = constraint_list
        self.event_count_matrix = []
        self.feature_list = []
        self.ecm = None
        if self.constraint_list is None:
            self.constraint_list = []
        self.ignore_list = ignore_list
        if self.ignore_list is None:
            self.ignore_list = []
        self.log_total = 0
        self.log_success = 0
        self.log_windows = 0

        self.persistence_file_name = AminerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)

        if persistence_data is not None:
            self.event_count_matrix = list(persistence_data)
            self.compute_pca()
            # Copy feature list into event count vector and reset counts of each feature
            self.event_count_vector = copy.deepcopy(self.event_count_matrix[0])
            self.reset_event_count_vector()
        else:
            if self.target_path_list is None or len(self.target_path_list) == 0:
                # Only one dimension when events are used instead of values; use empty string as placeholder
                self.event_count_vector = {'': {}}
            else:
                self.event_count_vector = {}

    def receive_atom(self, log_atom):
        """Receive parsed atom and the information about the parser match."""
        parser_match = log_atom.parser_match
        self.log_total += 1

        # Skip paths from ignore list.
        for ignore_path in self.ignore_list:
            if ignore_path in parser_match.get_match_dictionary().keys():
                return

        # get the timestamp of the first log to start the time-window-process (flag)
        if self.first_log:
            self.start_time = log_atom.get_timestamp()
            self.first_log = False

        current_time = log_atom.get_timestamp()
        while current_time >= (self.start_time + self.block_time):
            # PCA computation only possible when at least 3 vectors are present
            if len(self.event_count_matrix) >= 3:
                anomalyScore = self.anomalyScore()
                if anomalyScore > self.anomaly_score_threshold:
                    try:
                        data = log_atom.raw_data.decode(AminerConfig.ENCODING)
                    except UnicodeError:
                        data = repr(log_atom.raw_data)
                    if self.output_log_line:
                        original_log_line_prefix = self.aminer_config.config_properties.get(
                            CONFIG_KEY_LOG_LINE_PREFIX, DEFAULT_LOG_LINE_PREFIX)
                        sorted_log_lines = [log_atom.parser_match.match_element.annotate_match('') + os.linesep + original_log_line_prefix +
                                            data]
                    else:
                        sorted_log_lines = [data]
                    affected_paths = []
                    affected_values = []
                    affected_counts = []
                    for path, count_dict in self.event_count_vector.items():
                        affected_paths.append(path)
                        affected_values.append(list(count_dict.keys()))
                        affected_counts.append(list(count_dict.values()))
                    analysis_component = {'AffectedLogAtomPaths': affected_paths, 'AffectedLogAtomValues': affected_values,
                                          'AffectedValueCounts': affected_counts, 'AnomalyScore': anomalyScore[0]}
                    event_data = {'AnalysisComponent': analysis_component}
                    for listener in self.anomaly_event_handlers:
                        listener.receive_event('Analysis.%s' % self.__class__.__name__, 'PCA anomaly detected',
                                               sorted_log_lines, event_data, log_atom, self)
            self.log_windows += 1

            # Add new values to matrix in learn mode
            if self.auto_include_flag is True:
                if len(self.event_count_matrix) >= self.num_windows:
                    del self.event_count_matrix[0]
                self.event_count_matrix.append(copy.deepcopy(self.event_count_vector))
                # PCA computation only possible when at least 3 vectors are present
                if len(self.event_count_matrix) >= 3:
                    self.repair_dict()
                    self.compute_pca()

            # Set window end time for next iteration
            self.start_time += self.block_time
            # Reset count vector for next time window
            self.reset_event_count_vector()

        if self.target_path_list is None or len(self.target_path_list) == 0:
            # Event is defined by the full path of log atom.
            constraint_path_flag = False
            for constraint_path in self.constraint_list:
                if parser_match.get_match_dictionary().get(constraint_path) is not None:
                    constraint_path_flag = True
                    break
            if not constraint_path_flag and self.constraint_list != []:
                return
            log_event = tuple(parser_match.get_match_dictionary().keys())
            if log_event in self.event_count_vector['']:
                self.event_count_vector[''][log_event] += 1
            else:
                self.event_count_vector[''][log_event] = 1
        else:
            # Event is defined by values in paths
            all_values_none = True
            for path in self.target_path_list:
                match = parser_match.get_match_dictionary().get(path)
                if match is None:
                    continue
                matches = []
                if isinstance(match, list):
                    matches = match
                else:
                    matches.append(match)
                for match in matches:
                    if isinstance(match.match_object, bytes):
                        value = match.match_object.decode(AminerConfig.ENCODING)
                    else:
                        value = str(match.match_object)
                    if value is not None:
                        all_values_none = False
                    if path in self.event_count_vector:
                        if value in self.event_count_vector[path]:
                            self.event_count_vector[path][value] += 1
                        else:
                            self.event_count_vector[path][value] = 1
                    else:
                        self.event_count_vector[path] = {value: 1}
            if all_values_none is True:
                return

        self.log_success += 1

    def compute_pca(self):
        """Carry out PCA on current event count matrix."""
        # extract the features out of ecm into a list
        self.feature_list = []
        for events in self.event_count_matrix[0].values():
            for feature in events:
                self.feature_list.append(feature)

        # extract existing event_counts into array
        matrix = []
        for event_count in self.event_count_matrix:
            row = []
            for event in event_count.values():
                row += list(event.values())
            matrix.append(row)
        self.ecm = np.array(matrix)

        # Principial Component Analysis (PCA)
        normalized_ecm = (self.ecm - self.ecm.mean()) / self.ecm.std()
        covariance_matrix = np.cov(normalized_ecm.T)
        eigen_values, eigen_vectors = np.linalg.eigh(covariance_matrix)
        self.pca_ecm = normalized_ecm @ eigen_vectors
        self.eigen_vectors = eigen_vectors

        # number of components (nComp): how many components should be used for reconstruction
        self.nComp = self.get_nComp(eigen_values)

        # PCA Inverse with only these components which describes the variance_threshold
        pca_inverse = self.pca_ecm[:, :self.nComp] @ eigen_vectors[:self.nComp, :]

        # Calculate Anomaly-Score (Reconstruction Error) for the whole dataset
        self.loss = np.sum((normalized_ecm - pca_inverse)**2, axis=1)

    def anomalyScore(self):
        """Calculate the anomalyscore for current event_count_vector."""
        # convert the event_count_vector into an array
        ecv = self.vector2array()
        # normalize the ecv with the mean and std of learned ecm
        normalized_ecv = (ecv - self.ecm.mean()) / self.ecm.std()
        # reshape array into a 1-dimensional array
        normalized_ecv = normalized_ecv.reshape(1, -1)
        # calculate the reduced pca for current log-sequence with given eigen_vectors
        pca_ecv = normalized_ecv @ self.eigen_vectors
        # calculate the pca_inverse with reduced number of components / do reconstruction
        pca_inverse_ecv = pca_ecv[:, :self.nComp] @ self.eigen_vectors[:self.nComp, :]
        # calculate the reconstruction error / anomaly score
        loss = np.sum((normalized_ecv - pca_inverse_ecv)**2, axis=1)
        # scale the reconstruction error with the min, max of ecm-loss
        loss = (loss - np.min(self.loss)) / (np.max(self.loss) - np.min(self.loss))

        return loss

    def vector2array(self):
        """Extract only the values which were learned before from current self.event_count_vector and return an array."""
        vector = []
        for event in self.event_count_vector.values():
            for feature, value in event.items():
                if feature in self.feature_list:
                    vector.append(value)

        return np.array(vector)

    def get_nComp(self, eigen_values):
        """Return the number of components, which describe the variance threshold."""
        # Calculate the explained variance on each of components
        variance_explained = []
        for i in eigen_values[::-1]:
            variance_explained.append((i/sum(eigen_values))*100)
        # Calculate the cumulative explained variance (np.cumsum)
        cumulative_variance_explained = np.cumsum(variance_explained)
        for n, i in enumerate(cumulative_variance_explained):
            if i > (self.variance_threshold*100):
                return n

        return None

    def repair_dict(self):
        """Check if any new values were added in current event_count_vector and repair self.event_count_matrix when necessary."""
        for ecv in self.event_count_matrix:
            for key, value in self.event_count_vector.items():
                if key not in ecv.keys():
                    for val in value:
                        ecv[key] = {val: 0}
                if not self.event_count_vector[key].keys() == ecv[key].keys():
                    for k in self.event_count_vector[key].keys():
                        if k not in ecv[key].keys():
                            ecv[key][k] = 0

    def reset_event_count_vector(self):
        """Reset event_count_vector by setting all count-values to 0."""
        for events in self.event_count_vector.values():
            for value in events:
                events[value] = 0

    def get_time_trigger_class(self):  # skipcq: PYL-R0201
        """
        Get the trigger class this component should be registered for.
        This trigger is used only for persistence, so real-time triggering is needed.
        """
        return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

    def do_timer(self, trigger_time):
        """Check current ruleset should be persisted."""
        if self.next_persist_time is None:
            return 600

        delta = self.next_persist_time - trigger_time
        if delta < 0:
            self.do_persist()
            delta = 600

        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        if self.auto_include_flag is True:
            PersistenceUtil.store_json(self.persistence_file_name, list(self.event_count_matrix))
        self.next_persist_time = None

    def allowlist_event(self, event_type, event_data, allowlisting_data):
        """
        Allowlist an event generated by this source using the information emitted when generating the event.
        @return a message with information about allowlisting
        @throws Exception when allowlisting of this special event using given allowlisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if allowlisting_data is not None:
            msg = 'Allowlisting data not understood by this detector'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data not in self.constraint_list:
            self.constraint_list.append(event_data)
        return 'Allowlisted path %s.' % event_data

    def blocklist_event(self, event_type, event_data, blocklisting_data):
        """
        Blocklist an event generated by this source using the information emitted when generating the event.
        @return a message with information about blocklisting
        @throws Exception when blocklisting of this special event using given blocklisting_data was not possible.
        """
        if event_type != 'Analysis.%s' % self.__class__.__name__:
            msg = 'Event not from this source'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if blocklisting_data is not None:
            msg = 'Blocklisting data not understood by this detector'
            logging.getLogger(AminerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
        if event_data not in self.ignore_list:
            self.ignore_list.append(event_data)
        return 'Blocklisted path %s.' % event_data

    def log_statistics(self, component_name):
        """
        Log statistics of an AtomHandler. Override this method for more sophisticated statistics output of the AtomHandler.
        @param component_name the name of the component which is printed in the log line.
        """
        if STAT_LEVEL == 1:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully in %d time windows in the last 60"
                " minutes.", component_name, self.log_success, self.log_total, self.log_windows)
        elif STAT_LEVEL == 2:
            logging.getLogger(STAT_LOG_NAME).info(
                "'%s' processed %d out of %d log atoms successfully in %d time windows in the last 60"
                " minutes.", component_name, self.log_success, self.log_total, self.log_windows)
        self.log_success = 0
        self.log_total = 0
        self.log_windows = 0
