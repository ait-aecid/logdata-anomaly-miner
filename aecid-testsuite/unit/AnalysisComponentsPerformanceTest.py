import unittest
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from unit.TestBase import TestBase
from datetime import datetime
import time
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from aminer.analysis.AtomFilters import MatchPathFilter, SubhandlerFilter, \
    MatchValueFilter
from aminer.analysis.EnhancedNewMatchPathValueComboDetector import EnhancedNewMatchPathValueComboDetector
from aminer.analysis.HistogramAnalysis import ModuloTimeBinDefinition, \
    HistogramData, HistogramAnalysis
from aminer.parsing.MatchElement import MatchElement
import random
from aminer.analysis.MatchValueAverageChangeDetector import MatchValueAverageChangeDetector
from aminer.analysis.MatchValueStreamWriter import MatchValueStreamWriter
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from time import process_time
from aminer.analysis.MissingMatchPathValueDetector import MissingMatchPathListValueDetector
from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector
from aminer.analysis.TimeCorrelationDetector import TimeCorrelationDetector
from aminer.analysis.TimeCorrelationViolationDetector import CorrelationRule, \
    EventClassSelector, TimeCorrelationViolationDetector
from aminer.analysis.TimestampCorrectionFilters import SimpleMonotonicTimestampAdjust
from aminer.analysis import Rules
from aminer.analysis.TimestampsUnsortedDetector import TimestampsUnsortedDetector
from aminer.analysis.Rules import PathExistsMatchRule
from aminer.analysis.WhitelistViolationDetector import WhitelistViolationDetector
from _io import StringIO


class AnalysisComponentsPerformanceTest(TestBase):
    result_string = 'The %s could in average handle %d LogAtoms %s with %s\n'
    result = ''
    iterations = 2
    waiting_time = 1
    integerd = 'integer/d'
    different_pathes = '%d different path(es).'
    different_attributes = '%d different attribute(s).'

    @classmethod
    def tearDownClass(cls):
        super(AnalysisComponentsPerformanceTest, cls).tearDownClass()
        print('\nwaiting time: %d seconds' % cls.waiting_time)
        print(cls.result)

    def setUp(self):
        TestBase.setUp(self)
        self.output_stream = StringIO()
        self.stream_printer_event_handler = StreamPrinterEventHandler(self.analysis_context, self.output_stream)

    def run_atom_filters_match_path_filter(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            new_match_path_detector = NewMatchPathDetector(self.aminer_config,
                [self.stream_printer_event_handler], 'Default', True)
            subhandler_filter = SubhandlerFilter([], stop_when_handled_flag=True)
            i = 0
            while i < number_of_pathes:
                match_path_filter = MatchPathFilter([(self.integerd + str(i), new_match_path_detector)], None)
                subhandler_filter.add_handler(match_path_filter, stop_when_handled_flag=True)
                i = i + 1
            t = round(time.time(), 3)
            seconds = time.time();
            i = 0
            while int(time.time() - seconds) < self.waiting_time:
                decimal_integer_value_me = DecimalIntegerValueModelElement('d' + str(i % number_of_pathes),
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, match_path_filter)
                subhandler_filter.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (subhandler_filter.__class__.__name__, avg,
            results, '%d different %ss with a %s.' % (number_of_pathes, match_path_filter.__class__.__name__,
            new_match_path_detector.__class__.__name__))

    def run_atom_filters_match_value_filter(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            new_match_path_detector = NewMatchPathDetector(self.aminer_config,
                [self.stream_printer_event_handler], 'Default', True)
            subhandler_filter = SubhandlerFilter([], stop_when_handled_flag=True)
            i = 0
            dictionary = {}
            while i < 1000000:
                dictionary[i] = new_match_path_detector
                i = i + 1
            i = 0
            while i < number_of_pathes:
                match_value_filter = MatchValueFilter(self.integerd + str(i % number_of_pathes), dictionary, None)
                subhandler_filter.add_handler(match_value_filter, stop_when_handled_flag=True)
                i = i + 1
            t = round(time.time(), 3)
            seconds = time.time();
            i = 0
            while int(time.time() - seconds) < self.waiting_time:
                decimal_integer_value_me = DecimalIntegerValueModelElement('d' + str(i % number_of_pathes),
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, match_value_filter)
                subhandler_filter.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (subhandler_filter.__class__.__name__, avg,
            results, '%d different %ss with a dictionary of %ss.' % (number_of_pathes,
            match_value_filter.__class__.__name__, new_match_path_detector.__class__.__name__))

    def run_new_match_path_detector(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            new_match_path_detector = NewMatchPathDetector(self.aminer_config,
                [self.stream_printer_event_handler], 'Default', True)
            t = round(time.time(), 3)
            seconds = time.time();
            i = 0
            while int(time.time() - seconds) < self.waiting_time:
                decimal_integer_value_me = DecimalIntegerValueModelElement('d' + str(i % number_of_pathes),
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, new_match_path_detector)
                new_match_path_detector.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (new_match_path_detector.__class__.__name__,
            avg, results, self.different_pathes % number_of_pathes)

    def run_enhanced_new_match_path_value_combo_detector(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            i = 0
            path_list = []
            while i < number_of_pathes:
                path_list.append(self.integerd + str(i % number_of_pathes))
                i = i + 1
            enhanced_new_match_path_value_combo_detector = EnhancedNewMatchPathValueComboDetector(self.aminer_config,
                path_list, [self.stream_printer_event_handler], 'Default', True, True)
            t = round(time.time(), 3)
            seconds = time.time();
            i = 0
            while int(time.time() - seconds) < self.waiting_time:
                decimal_integer_value_me = DecimalIntegerValueModelElement('d' + str(i % number_of_pathes),
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i % number_of_pathes).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t,
                    enhanced_new_match_path_value_combo_detector)
                enhanced_new_match_path_value_combo_detector.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            enhanced_new_match_path_value_combo_detector.__class__.__name__,
            avg, results, self.different_attributes % number_of_pathes)

    def run_histogram_analysis(self, number_of_pathes, amplifier):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            modulo_time_bin_definition = ModuloTimeBinDefinition(86400, 86400 / number_of_pathes, 0, 1, number_of_pathes, False)
            histogram_data = HistogramData('match/crontab', modulo_time_bin_definition)
            histogram_analysis = HistogramAnalysis(self.aminer_config, [(histogram_data.property_path, modulo_time_bin_definition)],
                amplifier * self.waiting_time, [self.stream_printer_event_handler], False, 'Default')

            i = 0
            seconds = time.time();
            t = seconds
            while int(time.time() - seconds) < self.waiting_time:
                p = process_time()
                rand = random.randint(0, 100000)
                seconds = seconds + process_time() - p
                match_element = MatchElement('match/crontab', t + rand, t + rand, [])
                log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t + i, histogram_analysis)
                histogram_analysis.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (histogram_analysis.__class__.__name__,
            avg, results, '%d bin(s) and output after %d elements.' % (number_of_pathes, amplifier * self.waiting_time))

    def run_match_value_average_change_detector(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            i = 0
            path_list = []
            while i < number_of_pathes:
                path_list.append(self.integerd + str(i % number_of_pathes))
                i = i + 1
            seconds = time.time();
            t = time.time()
            match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config,
                [self.stream_printer_event_handler], None, path_list, 2, t, True, False, 'Default')
            i = 0
            while i < number_of_pathes:
                match_element = MatchElement(self.integerd + str(i), '%s' % str(t), t, [])
                log_atom = LogAtom(match_element.get_match_object(), ParserMatch(match_element), t,
                    match_value_average_change_detector)
                match_value_average_change_detector.receive_atom(log_atom)

                match_element = MatchElement(self.integerd + str(i), '%s' % str(t + 0.1), t + 0.1, [])
                log_atom = LogAtom(match_element.get_match_object(), ParserMatch(match_element), t + 0.1,
                    match_value_average_change_detector)
                match_value_average_change_detector.receive_atom(log_atom)

                match_element = MatchElement(self.integerd + str(i), '%s' % str(t + 0.2), t + 0.2, [])
                log_atom = LogAtom(match_element.get_match_object(), ParserMatch(match_element), t + 0.2,
                    match_value_average_change_detector)
                match_value_average_change_detector.receive_atom(log_atom)

                match_element = MatchElement(self.integerd + str(i), '%s' % str(t + 10), t + 10, [])
                log_atom = LogAtom(match_element.get_match_object(), ParserMatch(match_element), t + 10,
                    match_value_average_change_detector)
                match_value_average_change_detector.receive_atom(log_atom)
                i = i + 1

            i = 0
            t = time.time()
            while int(time.time() - seconds) < self.waiting_time:
                p = process_time()
                r = random.randint(0, 1) / 100 * 0.05
                seconds = seconds + p - process_time()
                delta = 0.15 + r
                match_element = MatchElement(self.integerd + str(i % number_of_pathes), '%s' % str(t + delta), t + delta, [])
                log_atom = LogAtom(match_element.get_match_object(), ParserMatch(match_element), t + delta,
                    match_value_average_change_detector)
                match_value_average_change_detector.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (match_value_average_change_detector.__class__.__name__,
            avg, results, self.different_pathes % number_of_pathes)

    def run_match_value_stream_writer(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            i = 0
            path_list = []
            parsing_model = []
            while i < number_of_pathes / 2:
                path_list.append('match/integer/d' + str(i % number_of_pathes))
                path_list.append('match/integer/s' + str(i % number_of_pathes))
                parsing_model.append(DecimalIntegerValueModelElement('d' + str(i % number_of_pathes),
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE))
                parsing_model.append(FixedDataModelElement('s' + str(i % number_of_pathes), b' Euro '))
                i = i + 1
            sequence_model_element = SequenceModelElement('integer', parsing_model)
            match_value_stream_writer = MatchValueStreamWriter(self.output_stream, path_list, b';', b'-')
            t = time.time()
            seconds = time.time();
            i = 0
            while int(time.time() - seconds) < self.waiting_time:
                data = b''
                p = process_time()
                for j in range(1, int(number_of_pathes / 2) + number_of_pathes % 2 + 1):
                    data = data + str(j).encode() + b' Euro '
                seconds = seconds + process_time() - p
                match_context = MatchContext(data)
                match_element = sequence_model_element.get_match_element('match', match_context)
                log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, match_value_stream_writer)
                match_value_stream_writer.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (match_value_stream_writer.__class__.__name__,
            avg, results, self.different_pathes % number_of_pathes)

    def run_missing_match_path_value_detector(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            i = 0
            path_list = []
            while i < number_of_pathes:
                path_list.append(self.integerd + str(i % number_of_pathes))
                i = i + 1
            missing_match_path_list_value_detector = MissingMatchPathListValueDetector(self.aminer_config,
                path_list, [self.stream_printer_event_handler], 'Default', True, 3600, 86400)
            seconds = time.time();
            t = seconds
            i = 0
            while int(time.time() - seconds) < self.waiting_time:
                decimal_integer_value_me = DecimalIntegerValueModelElement('d' + str(i % number_of_pathes),
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(1).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                p = process_time()
                r = random.randint(0, 100)
                seconds = seconds + process_time() - p
                delta = int(r / 100)
                t = t + 4000 * delta
                log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t,
                    missing_match_path_list_value_detector)
                missing_match_path_list_value_detector.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (missing_match_path_list_value_detector.__class__.__name__,
            avg, results, self.different_pathes % number_of_pathes)

    def run_new_match_path_value_combo_detector(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            i = 0
            path_list = []
            while i < number_of_pathes:
                path_list.append(self.integerd + str(i % number_of_pathes))
                i = i + 1
            new_match_path_value_combo_detector = NewMatchPathValueComboDetector(self.aminer_config,
                path_list, [self.stream_printer_event_handler], 'Default', True, True)
            t = time.time()
            seconds = time.time();
            i = 0
            while int(time.time() - seconds) < self.waiting_time:
                decimal_integer_value_me = DecimalIntegerValueModelElement('d' + str(i % number_of_pathes),
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i % 100).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t,
                    new_match_path_value_combo_detector)
                new_match_path_value_combo_detector.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (new_match_path_value_combo_detector.__class__.__name__,
            avg, results, self.different_attributes % number_of_pathes)

    def run_new_match_path_value_detector(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            i = 0
            path_list = []
            while i < number_of_pathes:
                path_list.append(self.integerd + str(i % number_of_pathes))
                i = i + 1
            new_match_path_value_detector = NewMatchPathValueDetector(self.aminer_config, path_list,
                [self.stream_printer_event_handler], 'Default', True, True)
            t = time.time()
            seconds = time.time();
            i = 0
            while int(time.time() - seconds) < self.waiting_time:
                decimal_integer_value_me = DecimalIntegerValueModelElement('d' + str(i % number_of_pathes),
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i % 100).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, new_match_path_value_detector)
                new_match_path_value_detector.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (new_match_path_value_detector.__class__.__name__,
            avg, results, self.different_attributes % number_of_pathes)

    def run_time_correlation_detector(self, number_of_rules):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            time_correlation_detector = TimeCorrelationDetector(self.aminer_config, 2, number_of_rules, 0,
                [self.stream_printer_event_handler], record_count_before_event=self.waiting_time * 9000)
            t = time.time()
            seconds = time.time();
            i = 0
            while int(time.time() - seconds) < self.waiting_time:
                decimal_integer_value_me = DecimalIntegerValueModelElement('d',
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i % 100).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, time_correlation_detector)
                time_correlation_detector.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (time_correlation_detector.__class__.__name__,
            avg, results, 'testCount=%d.' % number_of_rules)

    def run_time_correlation_violation_detector(self, chance):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            correlation_rule = CorrelationRule('Correlation', 0, chance, max_artefacts_a_for_single_b=1,
                artefact_match_parameters=[('/integer/d0', '/integer/d1')])
            a_class_selector = EventClassSelector('Selector1', [correlation_rule], None)
            b_class_selector = EventClassSelector('Selector2', None, [correlation_rule])
            rules = []
            rules.append(Rules.PathExistsMatchRule('/integer/d0', a_class_selector))
            rules.append(Rules.PathExistsMatchRule('/integer/d1', b_class_selector))

            time_correlation_violation_detector = TimeCorrelationViolationDetector(
                self.analysis_context.aminer_config, rules, [self.stream_printer_event_handler])
            seconds = time.time();
            s = seconds
            i = 0
            decimal_integer_value_me = DecimalIntegerValueModelElement('d0',
                DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
            while int(time.time() - seconds) < self.waiting_time:
                integer = '/integer'
                p = process_time()
                r = random.randint(1, 100)
                seconds = seconds + process_time() - p
                decimal_integer_value_me1 = DecimalIntegerValueModelElement('d1',
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me.get_match_element(integer, match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), s,
                    time_correlation_violation_detector)
                time_correlation_violation_detector.receive_atom(log_atom)

                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me1.get_match_element(integer, match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), s + r / 100,
                    time_correlation_violation_detector)
                time_correlation_violation_detector.receive_atom(log_atom)
                s = s + r / 100

                if r / 100 >= chance:
                    p = process_time()
                    match_context = MatchContext(str(i).encode())
                    match_element = decimal_integer_value_me.get_match_element(integer, match_context)
                    log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), s,
                        time_correlation_violation_detector)
                    time_correlation_violation_detector.receive_atom(log_atom)
                    seconds = seconds + process_time() - p
                time_correlation_violation_detector.do_timer(s)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (time_correlation_violation_detector.__class__.__name__,
            avg, results, '%d%% chance of not finding an element' % ((1 - chance) * 100))

    def run_timestamp_correction_filters(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            new_match_path_detector = NewMatchPathDetector(self.aminer_config,
                [self.stream_printer_event_handler], 'Default', True)
            simple_monotonic_timestamp_adjust = SimpleMonotonicTimestampAdjust([new_match_path_detector])

            seconds = time.time();
            i = 0
            while int(time.time() - seconds) < self.waiting_time:
                decimal_integer_value_me = DecimalIntegerValueModelElement('d' + str(i % number_of_pathes),
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                p = process_time()
                r = random.randint(1, 1000000)
                seconds = seconds + process_time() - p
                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), seconds - r,
                    simple_monotonic_timestamp_adjust)
                simple_monotonic_timestamp_adjust.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (simple_monotonic_timestamp_adjust.__class__.__name__,
            avg, results, 'a %s and %d different path(es).' % (new_match_path_detector.__class__.__name__, number_of_pathes))

    def run_timestamps_unsorted_detector(self, reset_factor):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            timestamps_unsorted_detector = TimestampsUnsortedDetector(self.aminer_config,
                [self.stream_printer_event_handler])
            seconds = time.time();
            s = seconds
            i = 0
            mini = 100
            while int(time.time() - seconds) < self.waiting_time:
                decimal_integer_value_me = DecimalIntegerValueModelElement('d',
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                p = process_time()
                r = random.randint(1, 100)
                seconds = seconds + process_time() - p
                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), s + min(r, mini),
                    timestamps_unsorted_detector)
                timestamps_unsorted_detector.receive_atom(log_atom)
                if mini > r:
                    mini = r
                else:
                    mini = mini + reset_factor
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (timestamps_unsorted_detector.__class__.__name__,
            avg, results, 'a resetFactor of %f.' % reset_factor)

    def run_whitelist_violation_detector(self, number_of_pathes, modulo_factor):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            i = 0
            rules = []
            while i < number_of_pathes:
                rules.append(PathExistsMatchRule(self.integerd + str(i % number_of_pathes), None))
                i = i + 1
            whitelist_violation_detector = WhitelistViolationDetector(self.aminer_config, rules,
                [self.stream_printer_event_handler])
            t = time.time()
            seconds = time.time();
            i = 0
            while int(time.time() - seconds) < self.waiting_time:
                p = process_time()
                r = random.randint(1, 100)
                if (r >= modulo_factor):
                    r = 2
                else:
                    r = 1
                seconds = seconds + process_time() - p
                decimal_integer_value_me = DecimalIntegerValueModelElement('d' + str(i % (number_of_pathes * r)),
                    DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i % 100).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, whitelist_violation_detector)
                whitelist_violation_detector.receive_atom(log_atom)
                i = i + 1
            results[z] = i
            z = z + 1
            avg = avg + i
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (whitelist_violation_detector.__class__.__name__,
            avg, results, '%d different PathExistsMatchRules and a moduloFactor of %d.' % (number_of_pathes, modulo_factor))

    def test01_atom_filters(self):
        self.run_atom_filters_match_path_filter(1)
        self.run_atom_filters_match_path_filter(30)
        self.run_atom_filters_match_path_filter(100)

        self.run_atom_filters_match_value_filter(1)
        self.run_atom_filters_match_value_filter(30)
        self.run_atom_filters_match_value_filter(100)

    def test02_enhanced_new_match_path_value_combo_detector(self):
        self.run_enhanced_new_match_path_value_combo_detector(1)
        self.run_enhanced_new_match_path_value_combo_detector(30)
        self.run_enhanced_new_match_path_value_combo_detector(100)

    def test03_histogram_analysis(self):
        # with reports
        self.run_histogram_analysis(1, 40000)
        self.run_histogram_analysis(30, 40000)
        self.run_histogram_analysis(100, 40000)

        # without reports
        self.run_histogram_analysis(1, 100000)
        self.run_histogram_analysis(30, 100000)
        self.run_histogram_analysis(100, 100000)

    def test04_match_value_average_change_detector(self):
        self.run_match_value_average_change_detector(1)
        self.run_match_value_average_change_detector(30)
        self.run_match_value_average_change_detector(100)

    def test05_match_value_stream_writer(self):
        self.run_match_value_stream_writer(1)
        self.run_match_value_stream_writer(30)
        self.run_match_value_stream_writer(100)

    def test06_missing_match_path_value_detector(self):
        self.run_missing_match_path_value_detector(1)
        self.run_missing_match_path_value_detector(30)
        self.run_missing_match_path_value_detector(100)

    def test07_new_match_path_detector(self):
        self.run_new_match_path_detector(1)
        self.run_new_match_path_detector(1000)
        self.run_new_match_path_detector(100000)

    def test08_new_match_path_value_combo_detector(self):
        self.run_new_match_path_value_combo_detector(1)
        self.run_new_match_path_value_combo_detector(30)
        self.run_new_match_path_value_combo_detector(100)

    def test09_new_match_path_value_detector(self):
        self.run_new_match_path_value_detector(1)
        self.run_new_match_path_value_detector(30)
        self.run_new_match_path_value_detector(100)

    def test10_time_correlation_detector(self):
        self.run_time_correlation_detector(1)
        self.run_time_correlation_detector(1000)
        self.run_time_correlation_detector(100000)

    def test11_time_correlation_violation_detector(self):
        self.run_time_correlation_violation_detector(0.99)
        self.run_time_correlation_violation_detector(0.95)
        self.run_time_correlation_violation_detector(0.50)
        self.run_time_correlation_violation_detector(0.01)

    def test12_timestamp_correction_filters(self):
        self.run_timestamp_correction_filters(1)
        self.run_timestamp_correction_filters(1000)
        self.run_timestamp_correction_filters(100000)

    def test13_timestamps_unsorted_detector(self):
        self.run_timestamps_unsorted_detector(0.001)
        self.run_timestamps_unsorted_detector(0.1)
        self.run_timestamps_unsorted_detector(1)
        self.run_timestamps_unsorted_detector(100)

    def test14_whitelist_violation_detector(self):
        self.run_whitelist_violation_detector(1, 99)
        self.run_whitelist_violation_detector(1, 50)
        self.run_whitelist_violation_detector(1, 1)
        self.run_whitelist_violation_detector(1000, 99)
        self.run_whitelist_violation_detector(1000, 50)
        self.run_whitelist_violation_detector(1000, 1)
        self.run_whitelist_violation_detector(100000, 99)
        self.run_whitelist_violation_detector(100000, 50)
        self.run_whitelist_violation_detector(100000, 1)


if __name__ == '__main__':
    unittest.main()