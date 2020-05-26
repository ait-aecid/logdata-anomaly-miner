"""This component performs a histogram analysis on one or more input
properties. The properties are parsed values denoted by their
parsing path. Those values are then handed over to the selected
"binning function", that calculates the histogram bin.

* Binning:

Binning can be done using one of the predefined binning functions
or by creating own subclasses from "HistogramAnalysis.BinDefinition".

  * LinearNumericBinDefinition: Binning function working on numeric
    values and sorting them into bins of same size.

  * ModuloTimeBinDefinition: Binning function working on parsed
    datetime values but applying a modulo function to them. This
    is useful for analysis of periodic activities.


* Example:

The following example creates a HistogramAnalysis using only the
property "/model/line/time", binned on per-hour basis and sending
a report every week:

  from aminer.analysis import HistogramAnalysis
  # Use a time-modulo binning function
  moduloTimeBinDefinition=HistogramAnalysis.ModuloTimeBinDefinition(
      3600*24, # Modulo values in seconds (1 day)
      3600,    # Division factor to get down to reporting unit (1h)
      0,       # Start of lowest bin
      1,       # Size of bin in reporting units
      24,      # Number of bins
      False)   # Disable outlier bins, not possible with time modulo
  histogramAnalysis=HistogramAnalysis.HistogramAnalysis(
      aminer_config,
      [('/model/line/time', moduloTimeBinDefinition)],
      3600*24*7,  # Reporting interval (weekly)
      report_event_handlers,        # Send report to those handlers
      reset_after_report_flag=True)  # Zero counters after sending of report
  # Send the appropriate input feed to the component
  atomFilter.addHandler(histogramAnalysis)
"""

import time
import os
from datetime import datetime

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface

binomial_test = None
try:
    from scipy import stats

    binomial_test = stats.binom_test
# skipcq: FLK-E722
except:
    pass

date_string = "%Y-%m-%d %H:%M:%S"


class BinDefinition:
    not_implemented = 'Not implemented'
    """This class defines the bins of the histogram."""

    def __init__(self):
        raise Exception(self.not_implemented)

    def has_outlier_bins(self):
        """Report if this binning works with outlier bins, that are bins for all values outside the normal binning range. If not,
        outliers are discarded. When true, the outlier bins are the first and last bin."""
        raise Exception(self.not_implemented)

    def get_bin_names(self):
        """Get the names of the bins for reporting, including the outlier bins if any."""
        raise Exception(self.not_implemented)

    def get_bin(self, value):
        """Get the number of the bin this value should belong to.
        @return the bin number or None if the value is an outlier and outlier bins were not requested. With outliers, bin 0
        is the bin with outliers below limit, first normal bin is at index 1."""
        raise Exception(self.not_implemented)

    # skipcq: PYL-W0613, PYL-R0201
    def get_bin_p_value(self, bin_pos, total_values, bin_values):
        """Calculate a p-Value, how likely the observed number of
        elements in this bin is. This method is used as an interface method, but it also returns a default value.
        @return the value or None when not applicable."""
        return None


class LinearNumericBinDefinition(BinDefinition):
    """This class defines the linear numeric bins."""

    # skipcq: PYL-W0231
    def __init__(self, lower_limit, bin_size, bin_count, outlier_bins_flag=False):
        self.lower_limit = lower_limit
        self.bin_size = bin_size
        self.bin_count = bin_count
        self.outlier_bins_flag = outlier_bins_flag
        self.bin_names = None
        self.expected_bin_ratio = 1.0 / float(bin_count)

    def has_outlier_bins(self):
        """Report if this binning works with outlier bins, that are bins for all values outside the normal binning range. If not,
        outliers are discarded. When true, the outlier bins are the first and last bin."""
        return self.outlier_bins_flag

    def get_bin_names(self):
        """Get the names of the bins for reporting, including the outlier bins if any."""
        # Cache the names here so that multiple histograms using same
        # BinDefinition do not use separate copies of the strings.
        if self.bin_names is not None:
            return self.bin_names
        self.bin_names = []
        if self.outlier_bins_flag:
            self.bin_names.append('...-%s]' % self.lower_limit)
        start = self.lower_limit
        for bin_pos in range(1, self.bin_count + 1):
            end = self.lower_limit + bin_pos * self.bin_size
            self.bin_names.append('[%s-%s]' % (start, end))
            start = end
        if self.outlier_bins_flag:
            self.bin_names.append('[%s-...' % start)
        return self.bin_names

    def get_bin(self, value):
        """Get the number of the bin this value should belong to.
        @return the bin number or None if the value is an outlier and outlier bins were not requested. With outliers, bin 0
        is the bin with outliers below limit, first normal bin is at index 1."""
        if self.outlier_bins_flag:
            if value < self.lower_limit:
                return 0
            pos = int((value - self.lower_limit) / self.bin_size)
            if pos < self.bin_count:
                return pos + 1
            return self.bin_count + 1

        if value < self.lower_limit:
            return None
        pos = int((value - self.lower_limit) / self.bin_size)
        if pos < self.bin_count:
            return pos
        return None

    def get_bin_p_value(self, bin_pos, total_values, bin_values):
        """Calculate a p-Value, how likely the observed number of elements in this bin is.
        @return the value or None when not applicable."""
        if binomial_test is None:
            return None
        if self.outlier_bins_flag:
            if (bin_pos == 0) or (bin_pos > self.bin_count):
                return None
        return binomial_test(bin_values, total_values, self.expected_bin_ratio)


class ModuloTimeBinDefinition(LinearNumericBinDefinition):
    """This class defines the module time bins."""

    def __init__(self, modulo_value, time_unit, lower_limit, bin_size, bin_count, outlier_bins_flag=False):
        super(ModuloTimeBinDefinition, self).__init__(lower_limit, bin_size, bin_count, outlier_bins_flag)
        self.modulo_value = modulo_value
        self.time_unit = time_unit

    def get_bin(self, value):
        """Get the number of the bin this value should belong to.
        @return the bin number or None if the value is an outlier and outlier bins were not requested. With outliers, bin 0
        is the bin with outliers below limit, first normal bin is at index 1."""
        if value is None:
            value = 0
        if isinstance(value, bytes):
            value = int.from_bytes(value, 'big')
            return super(ModuloTimeBinDefinition, self).get_bin(value)
        if isinstance(value, str):
            value = int.from_bytes(value.encode(), 'big')
            return super(ModuloTimeBinDefinition, self).get_bin(value)
        time_value = (value % self.modulo_value) / self.time_unit
        return super(ModuloTimeBinDefinition, self).get_bin(time_value)


class HistogramData():
    """This class defines the properties of one histogram to create and performs the accounting and reporting. When the Python scipy
    package is available, reports will also include probability score created using binomial testing."""

    def __init__(self, property_path, bin_definition):
        """Create the histogram data structures.
        @param lower_limit the lowest value included in the first bin."""
        self.property_path = property_path
        self.bin_definition = bin_definition
        self.bin_names = bin_definition.get_bin_names()
        self.bin_data = [0] * (len(self.bin_names))
        self.has_outlier_bins_flag = bin_definition.has_outlier_bins()
        self.total_elements = 0
        self.binned_elements = 0

    def add_value(self, value):
        """Add one value to the histogram."""
        bin_pos = self.bin_definition.get_bin(value)
        self.bin_data[bin_pos] += 1
        self.total_elements += 1
        if (self.has_outlier_bins_flag) and (bin_pos != 0) and (bin_pos + 1 != len(self.bin_names)):
            self.binned_elements += 1

    def reset(self):
        """Remove all values from this histogram."""
        self.total_elements = 0
        self.binned_elements = 0
        self.bin_data = [0] * (len(self.bin_data))

    def clone(self):
        """Clone this object so that calls to addValue do not influence the old object any more. This behavior is a mixture of shallow
        and deep copy."""
        histogram_data = HistogramData(self.property_path, self.bin_definition)
        histogram_data.bin_names = self.bin_names
        histogram_data.bin_data = self.bin_data[:]
        histogram_data.total_elements = self.total_elements
        histogram_data.binned_elements = self.binned_elements
        return histogram_data

    def to_string(self, indent):
        """Get a string representation of this histogram."""
        result = '%sProperty "%s" (%d elements):' % (indent, self.property_path, self.total_elements)
        f_elements = float(self.total_elements)
        base_element = self.binned_elements if self.has_outlier_bins_flag else self.total_elements
        for bin_pos in range(0, len(self.bin_data)):
            count = self.bin_data[bin_pos]
            if count == 0:
                continue
            p_value = self.bin_definition.get_bin_p_value(bin_pos, base_element, count)
            if p_value is None:
                result += '\n%s* %s: %d (ratio = %.2e)' % (indent, self.bin_names[bin_pos], count, float(count) / f_elements)
            else:
                result += '\n%s* %s: %d (ratio = %.2e, p = %.2e)' % \
                          (indent, self.bin_names[bin_pos], count, float(count) / f_elements, p_value)
        return result


class HistogramAnalysis(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class creates a histogram for one or more properties extracted from a parsed atom."""

    def __init__(self, aminer_config, histogram_defs, report_interval, report_event_handlers, reset_after_report_flag=True,
                 persistence_id='Default', output_log_line=True):
        """Initialize the analysis component.
        @param histogram_defs is a list of tuples containing the target property path to analyze and the BinDefinition to apply for
        binning.
        @param report_interval delay in seconds between creation of two reports. The parameter is applied to the parsed record data
        time, not the system time. Hence reports can be delayed when no data is received."""
        self.last_report_time = None
        self.next_report_time = 0.0
        self.histogram_data = []
        for (path, bin_definition) in histogram_defs:
            self.histogram_data.append(HistogramData(path, bin_definition))
        self.report_interval = report_interval
        self.report_event_handlers = report_event_handlers
        self.reset_after_report_flag = reset_after_report_flag
        self.persistence_id = persistence_id
        self.next_persist_time = None
        self.output_log_line = output_log_line

        PersistencyUtil.add_persistable_component(self)
        self.persistenceFileName = AMinerConfig.build_persistence_file_name(aminer_config, 'HistogramAnalysis', persistence_id)
        persistence_data = PersistencyUtil.load_json(self.persistenceFileName)
        if persistence_data is not None:
            raise Exception('No data reading, def merge yet')

    def receive_atom(self, log_atom):
        match_dict = log_atom.parser_match.get_match_dictionary()
        data_updated_flag = False
        for data_item in self.histogram_data:
            match = match_dict.get(data_item.property_path, None)
            if match is None:
                continue
            data_updated_flag = True
            data_item.add_value(match.match_object)

        timestamp = log_atom.get_timestamp()
        if timestamp is None:
            timestamp = time.time()
        if self.next_report_time < timestamp:
            if self.last_report_time is None:
                self.last_report_time = timestamp
                self.next_report_time = timestamp + self.report_interval
            else:
                self.send_report(log_atom, timestamp)

        if self.next_persist_time is None and data_updated_flag:
            self.next_persist_time = time.time() + 600

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
            self.do_persist()
            delta = 600
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        # PersistencyUtil.storeJson(self.persistence_file_name, list(self.knownPathSet))
        self.next_persist_time = None

    def send_report(self, log_atom, timestamp):
        """Sends a report to the event handlers."""
        report_str = 'Histogram report '
        if self.last_report_time is not None:
            report_str += 'from %s ' % datetime.fromtimestamp(self.last_report_time).strftime(date_string)
        report_str += 'till %s' % datetime.fromtimestamp(timestamp).strftime(date_string)
        affected_log_atom_pathes = []
        analysis_component = {'AffectedLogAtomPathes': affected_log_atom_pathes}
        for histogramData in self.histogram_data:
            affected_log_atom_pathes.append(histogramData.property_path)
        res = []
        h = []
        for data_item in self.histogram_data:
            d = {}
            bins = {}
            i = 0
            while i < len(data_item.bin_names):
                bins[data_item.bin_names[i]] = data_item.bin_data[i]
                i = i + 1
            d['TotalElements'] = data_item.total_elements
            d['BinnedElements'] = data_item.binned_elements
            d['HasOutlierBinsFlag'] = data_item.has_outlier_bins_flag
            d['Bins'] = bins
            if self.output_log_line:
                bin_definition = {
                  'Type': str(data_item.bin_definition.__class__.__name__),
                  'LowerLimit': data_item.bin_definition.lower_limit, 'BinSize': data_item.bin_definition.bin_size,
                  'BinCount': data_item.bin_definition.bin_count, 'OutlierBinsFlag': data_item.bin_definition.outlier_bins_flag,
                  'BinNames': data_item.bin_definition.bin_names, 'ExpectedBinRatio': data_item.bin_definition.expected_bin_ratio}
                if isinstance(data_item.bin_definition, ModuloTimeBinDefinition):
                    bin_definition['ModuloValue'] = data_item.bin_definition.modulo_value
                    bin_definition['TimeUnit'] = data_item.bin_definition.time_unit
                d['BinDefinition'] = bin_definition
                match_paths_values = {}
                for match_path, match_element in log_atom.parser_match.get_match_dictionary().items():
                    match_value = match_element.match_object
                    if isinstance(match_value, bytes):
                        match_value = match_value.decode()
                    match_paths_values[match_path] = match_value
                analysis_component['ParsedLogAtom'] = match_paths_values
            d['PropertyPath'] = data_item.property_path
            for line in data_item.to_string('  ').split('\n'):
                report_str += os.linesep + line
            res += [''] * data_item.total_elements
            h.append(d)
        analysis_component['HistogramData'] = h
        analysis_component['ReportInterval'] = self.report_interval
        analysis_component['ResetAfterReportFlag'] = self.reset_after_report_flag
        event_data = {'AnalysisComponent': analysis_component}
        if len(res) > 0:
            res[0] = report_str
            for listener in self.report_event_handlers:
                listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Histogram report', res, event_data, log_atom, self)
        if self.reset_after_report_flag:
            for data_item in self.histogram_data:
                data_item.reset()

        self.last_report_time = timestamp
        self.next_report_time = timestamp + self.report_interval


class PathDependentHistogramAnalysis(AtomHandlerInterface, TimeTriggeredComponentInterface):
    """This class provides a histogram analysis for only one property but separate histograms for each group of correlated match pathes.
    Assume there two pathes that include the requested property but they separate after the property was found on the path.
    Then objects of this class will produce 3 histograms: one for common path part including all occurences of the target property
    and one for each separate subpath, counting only those property values where the specific subpath was followed."""

    def __init__(self, aminer_config, property_path, bin_definition, report_interval, report_event_handlers, reset_after_report_flag=True,
                 persistence_id='Default', output_log_line=True):
        """Initialize the analysis component.
        @param report_interval delay in seconds between creation of two reports. The parameter is applied to the parsed record data
        time, not the system time. Hence reports can be delayed when no data is received."""
        self.last_report_time = None
        self.next_report_time = 0.0
        self.property_path = property_path
        self.bin_definition = bin_definition
        self.histogram_data = {}
        self.report_interval = report_interval
        self.report_event_handlers = report_event_handlers
        self.reset_after_report_flag = reset_after_report_flag
        self.persistence_id = persistence_id
        self.next_persist_time = None
        self.output_log_line = output_log_line

        PersistencyUtil.add_persistable_component(self)
        self.persistence_file_name = AMinerConfig.build_persistence_file_name(aminer_config, 'PathDependentHistogramAnalysis',
                                                                              persistence_id)
        persistence_data = PersistencyUtil.load_json(self.persistence_file_name)
        if persistence_data is not None:
            raise Exception('No data reading, def merge yet')

    def receive_atom(self, log_atom):
        match_dict = log_atom.parser_match.get_match_dictionary()
        match = match_dict.get(self.property_path, None)
        if match is None:
            return
        match_value = match.match_object

        all_path_set = set(match_dict.keys())
        unmapped_path = []
        missing_pathes = set()
        while all_path_set:
            path = all_path_set.pop()
            histogram_mapping = self.histogram_data.get(path, None)
            if histogram_mapping is None:
                unmapped_path.append(path)
                continue
            # So the path is already mapped to one histogram. See if all pathes
            # to the given histogram are still in all_path_set. If not, a split
            # within the mapping is needed.
            clone_set = all_path_set.copy()
            mapped_path = None
            for mapped_path in histogram_mapping[0]:
                try:
                    clone_set.remove(mapped_path)
                # skipcq: FLK-E722
                except:
                    if mapped_path != path:
                        missing_pathes.add(mapped_path)
            if not missing_pathes:
                # Everything OK, just add the value to the mapping.
                match = match_dict.get(mapped_path, None)
                match_value = match.match_object
                if isinstance(match.match_object, bytes):
                    match.match_object = match.match_object.decode()
                histogram_mapping[1].propertyPath = mapped_path
                histogram_mapping[1].add_value(match_value)
                histogram_mapping[2] = log_atom.parser_match
            else:
                # We need to split the current set here. Keep the current statistics
                # for all the missingPathes but clone the data for the remaining
                # pathes.
                new_histogram = histogram_mapping[1].clone()
                match = match_dict.get(mapped_path, None)
                match_value = match.match_object
                histogram_mapping[1].propertyPath = mapped_path
                new_histogram.add_value(match_value)
                new_path_set = histogram_mapping[0] - missing_pathes
                new_histogram_mapping = [new_path_set, new_histogram, log_atom.parser_match]
                for mapped_path in new_path_set:
                    self.histogram_data[mapped_path] = new_histogram_mapping
                histogram_mapping[0] = missing_pathes
                missing_pathes = set()

        if unmapped_path:
            histogram = HistogramData(self.property_path, self.bin_definition)
            histogram.add_value(match_value)
            new_record = [set(unmapped_path), histogram, log_atom.parser_match]
            for path in unmapped_path:
                new_record[1].property_path = path
                self.histogram_data[path] = new_record

        timestamp = log_atom.get_timestamp()
        if timestamp is None:
            timestamp = time.time()
        if self.next_report_time < timestamp:
            if self.last_report_time is None:
                self.last_report_time = timestamp
                self.next_report_time = timestamp + self.report_interval
            else:
                self.send_report(log_atom, timestamp)

        if self.next_persist_time is None:
            self.next_persist_time = time.time() + 600

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
            self.do_persist()
            delta = 600
        return delta

    def do_persist(self):
        """Immediately write persistence data to storage."""
        # PersistencyUtil.storeJson(self.persistence_file_name, list(self.knownPathSet))
        self.next_persist_time = None

    def send_report(self, log_atom, timestamp):
        """Send report to event handlers."""
        report_str = 'Path histogram report '
        if self.last_report_time is not None:
            report_str += 'from %s ' % datetime.fromtimestamp(self.last_report_time).strftime(date_string)
        report_str += 'till %s' % datetime.fromtimestamp(timestamp).strftime(date_string)
        all_path_set = set(self.histogram_data.keys())
        analysis_component = {'AffectedLogAtomPathes': list(all_path_set)}
        res = []
        h = []
        while all_path_set:
            d = {}
            path = all_path_set.pop()
            histogram_mapping = self.histogram_data.get(path)
            data_item = histogram_mapping[1]
            bins = {}
            i = 0
            while i < len(data_item.bin_names):
                bins[data_item.bin_names[i]] = data_item.bin_data[i]
                i = i + 1
            d['TotalElements'] = data_item.total_elements
            d['BinnedElements'] = data_item.binned_elements
            d['HasOutlierBinsFlag'] = data_item.has_outlier_bins_flag
            d['Bins'] = bins
            if self.output_log_line:
                match_paths_values = {}
                for match_path, match_element in log_atom.parser_match.get_match_dictionary().items():
                    match_value = match_element.match_object
                    if isinstance(match_value, datetime):
                        match_value = match_value.timestamp()
                    if isinstance(match_value, bytes):
                        match_value = match_value.decode()
                    match_paths_values[match_path] = match_value
                analysis_component['ParsedLogAtom'] = match_paths_values
                bin_definition = {
                  'Type': str(data_item.bin_definition.__class__.__name__),
                  'LowerLimit': data_item.bin_definition.lower_limit, 'BinSize': data_item.bin_definition.bin_size,
                  'BinCount': data_item.bin_definition.bin_count, 'OutlierBinsFlag': data_item.bin_definition.outlier_bins_flag,
                  'BinNames': data_item.bin_definition.bin_names, 'ExpectedBinRatio': data_item.bin_definition.expected_bin_ratio}
                if isinstance(data_item.bin_definition, ModuloTimeBinDefinition):
                    bin_definition['ModuloValue'] = data_item.bin_definition.modulo_value
                    bin_definition['TimeUnit'] = data_item.bin_definition.time_unit
                d['BinDefinition'] = bin_definition
            d['PropertyPath'] = data_item.propertyPath
            report_str += os.linesep + 'Path values "%s":' % '", "'.join(histogram_mapping[0])
            if isinstance(histogram_mapping[2].match_element.match_string, bytes):
                histogram_mapping[2].match_element.match_string = histogram_mapping[2].match_element.match_string.decode()
            report_str += os.linesep + 'Example: %s' % histogram_mapping[2].match_element.match_string
            if len(res) < histogram_mapping[1].total_elements:
                res = [''] * histogram_mapping[1].total_elements
            for line in histogram_mapping[1].to_string('  ').split('\n'):
                report_str += os.linesep + '%s' % line
            if len(res) > 0:
                res[0] = report_str
            all_path_set.discard(path)
            h.append(d)
        analysis_component['MissingPathes'] = list(histogram_mapping[0])
        analysis_component['HistogramData'] = h
        analysis_component['ReportInterval'] = self.report_interval
        analysis_component['ResetAfterReportFlag'] = self.reset_after_report_flag
        event_data = {'AnalysisComponent': analysis_component}

        if self.reset_after_report_flag:
            histogram_mapping[1].reset()
        for listener in self.report_event_handlers:
            listener.receive_event('Analysis.%s' % self.__class__.__name__, 'Histogram report', res, event_data, log_atom, self)

        self.last_report_time = timestamp
        self.next_report_time = timestamp + self.report_interval
