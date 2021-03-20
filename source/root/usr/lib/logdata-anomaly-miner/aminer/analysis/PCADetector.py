"""
This module defines a detector for new values in a data path.

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
import sys
import copy
import numpy as np

from aminer import AminerConfig
from aminer.AminerConfig import STAT_LEVEL, STAT_LOG_NAME, CONFIG_KEY_LOG_LINE_PREFIX
from aminer.AnalysisChild import AnalysisContext
from aminer.util import PersistenceUtil
from aminer.events.EventInterfaces import EventSourceInterface
from aminer.input.InputInterfaces import AtomHandlerInterface
from aminer.util.TimeTriggeredComponentInterface import TimeTriggeredComponentInterface



class PCADetector(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class creates events when new values for a given data path were found."""


    def __init__(self, aminer_config, target_path_list, anomaly_event_handlers, time_window, anomaly_score, variance,
                persistence_id='Default', auto_include_flag=False, output_log_line=True):
        """Initialize the detector. This will also trigger reading or creation of persistence storage location."""
        self.target_path_list = target_path_list
        self.anomaly_event_handlers = anomaly_event_handlers
        self.auto_include_flag = auto_include_flag
        self.next_persist_time = None
        self.output_log_line = output_log_line
        self.aminer_config = aminer_config
        self.persistence_id = persistence_id

        # window size in seconds
        self.block_time = time_window

        # threshold for anomaly score
        self.anomalyScore_threshold = anomaly_score
        
        # define the threshold for the variance, which is used to get to get the number of components (nComp)
        variance_threshold = variance

        # define flag for first log
        self.first_log = True
        # define variable for start time of window
        self.start_time = 0
       

        self.persistence_file_name = AminerConfig.build_persistence_file_name(aminer_config, self.__class__.__name__, persistence_id)
        PersistenceUtil.add_persistable_component(self)        
        persistence_data = PersistenceUtil.load_json(self.persistence_file_name)
        
        # self.auto_include_flag => learn_mode
        if self.auto_include_flag == True: 
            self.event_count_matrix = list()
            self.event_count_vector = dict()
        else:
            if persistence_data == None:
                print("No event count matrix available. Please run the aminer first with learn_mode = True")
            self.event_count_matrix = list(persistence_data) 
            self.event_count_vector = copy.deepcopy(self.event_count_matrix[0])
            self.reset_event_count_vector()
            
            # extract the features out of ecm into a list
            self.feature_list = list()
            for events in self.event_count_vector.values():
                for feature in events:
                    self.feature_list.append(feature)

            # extract existing event_counts into array
            matrix = list()
            for event_count in self.event_count_matrix:
                row = list()
                for event in event_count.values():
                    row += list(event.values())
                matrix.append(row)
                
            # self.ecm => extracted event_count_matrix (array)
            self.ecm = np.array(matrix)

            # Principial Component Analysis (PCA)
            normalized_ecm = (self.ecm - self.ecm.mean()) / self.ecm.std()
            covariance_matrix = np.cov(normalized_ecm.T)
            # use np.linalg.eigh for complex hermitian (conjugate symmetric) 
            eigen_values, eigen_vectors = np.linalg.eigh(covariance_matrix)
            self.pca_ecm = normalized_ecm @ eigen_vectors
            self.eigen_vectors = eigen_vectors
            
            # number of components (nComp): how many components should be used for reconstruction 
            self.nComp = self.get_nComp(eigen_values, variance_threshold)
            
            # PCA Inverse with only these components which describes the variance_threshold
            pca_inverse = self.pca_ecm[:,:self.nComp] @ eigen_vectors[:self.nComp,:]
            
            # Calculate Anomaly-Score (Reconstruction Error) for the whole dataset
            self.loss = np.sum((normalized_ecm - pca_inverse)**2, axis=1)


    def receive_atom(self, log_atom):
        """Receive parsed atom and the information about the parser match.
        @param log_atom the parsed log atom"""

        # get log_atom as dictionary
        match_dict = log_atom.parser_match.get_match_dictionary()
        
        # get the timestamp of the first log to start the time-window-process (flag)
        if self.first_log:
            self.start_time = log_atom.get_timestamp()
            self.first_log = False

        # get the timestamp (in seconds) of the receveived log_atom.object
        current_time = log_atom.get_timestamp()

        # Build Time-Windows (window_size = block_time)
        while current_time >= (self.start_time + self.block_time):

            # append event_count_vector into event_count_matrix (deepcopy)
            self.event_count_matrix.append(copy.deepcopy(self.event_count_vector))
            
            # if learn_mode == False: calculate anomaly-score
            if self.auto_include_flag == False:  
                anomalyScore = self.anomalyScore()
                # if the anomaly score is higher than a given threshold, print out the detection
                if anomalyScore > self.anomalyScore_threshold:
                    sorted_log_lines = list(log_atom.raw_data)
                    timestamp_from = time.strftime('%d/%b/%Y:%H:%M:%S', time.gmtime(self.start_time))
                    timestamp_to = time.strftime('%d/%b/%Y:%H:%M:%S', time.gmtime(current_time))
                    analysis_component = {'AffectedTimeWindow': {'from':timestamp_from,'to':timestamp_to}, 'AnomalyScore': anomalyScore[0]}
                    event_data = {'AnalysisComponent': analysis_component}
                    print(analysis_component)
                    for listener in self.anomaly_event_handlers:
                        listener.receive_event('Analysis.%s' % self.__class__.__name__, 'New anomalous timewindow detected', sorted_log_lines, event_data, log_atom, self)
                        
            # repair self.event_count_matrix, if new values occured
            self.repair_dict()
            # set time window to next block_time
            self.start_time += self.block_time            
            # reset self.event_count_vector for new time window
            self.reset_event_count_vector()                   

        # Let's go through the received log_atom and build the event_count_vector 
        for path, match in match_dict.items():
            # go trough all features in paths (specified in /etc/aminer/config.yml)
            if path in self.target_path_list:
                # create a dict of dicts = {path:{value:counter}}
                if path not in self.event_count_vector:
                    self.event_count_vector.update({path:{match.match_string.decode():1}})	
                else:
                    # if value does exist, increment counter
                    if match.match_string.decode() in self.event_count_vector[path]:
                        self.event_count_vector[path][match.match_string.decode()] += 1
                    # if value does not exist, create new value
                    else:
                        self.event_count_vector[path][match.match_string.decode()] = 1


    ##### ANOMALY-SCORE FUNCTIONS #####       
    def anomalyScore(self):
        """calculate the anomalyscore for current event_count_vector"""
        ecv = self.vector2array()
        normalized_ecv = (ecv - self.ecm.mean()) / self.ecm.std()
        normalized_ecv = normalized_ecv.reshape(1,-1)
        # calculate the reduced pca for current log-sequence with given eigen_vectors
        pca_ecv = normalized_ecv @ self.eigen_vectors
        # calculate the pca_inverse with reduced number of components / do reconstruction
        pca_inverse_ecv = pca_ecv[:,:self.nComp] @ self.eigen_vectors[:self.nComp,:]
        # calculate the reconstruction error / anomaly score
        loss = np.sum((normalized_ecv - pca_inverse_ecv)**2, axis=1)
        # scale the reconstruction error with the min, max of ecm-loss
        loss = (loss - np.min(self.loss)) / (np.max(self.loss) - np.min(self.loss))
        return loss

    def vector2array(self):
        """extract only the values which were learned before out of current
        self.event_count_vector (dictionary of dictionaries) into array"""
        vector = list()
        for event in self.event_count_vector.values():
            for feature, value in event.items():
                if feature in self.feature_list:
                    vector.append(value)
        return np.array(vector)
        
    def get_nComp(self, eigen_values, variance_threshold=0.98):
        """return the number of components, which describe the variance threshold"""
        # Calculate the explained variance on each of components
        variance_explained = []
        for i in eigen_values[::-1]:
            variance_explained.append((i/sum(eigen_values))*100)
        # Calculate the cumulative explained variance (np.cumsum)
        cumulative_variance_explained = np.cumsum(variance_explained)
        for n, i in enumerate(cumulative_variance_explained):
            if i > (variance_threshold*100):
                return n     
    

    ##### EVENT VECTOR FUNTIONS #####                     
    def repair_dict(self):
        """check if the dictionary-values in event_count_matrix are consistent 
        with current event_count_vector and repair it when necessary"""
        for ecv in self.event_count_matrix:
            for key,value in self.event_count_vector.items():
                if key not in ecv.keys():
                    for val in value:
                        ecv[key] = {val:0}
                if not self.event_count_vector[key].keys() == ecv[key].keys():
                    for k in self.event_count_vector[key].keys():
                        if k not in ecv[key].keys():
                            ecv[key][k] = 0

    def reset_event_count_vector(self):
        """reset event_count_vector by setting all count-values to 0"""
        for events in self.event_count_vector.values():
                for value in events:
                    events[value] = 0 
                    
                          
    ##### BUILT-IN DETECTOR FUNTIONS #####                     
    def get_time_trigger_class(self):
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
        if self.auto_include_flag: 
            PersistenceUtil.store_json(self.persistence_file_name, list(self.event_count_matrix))
        self.next_persist_time = None









