import unittest
from aminer.analysis import NewMatchPathDetector, MatchValueAverageChangeDetector, MatchValueStreamWriter, \
    MissingMatchPathListValueDetector, NewMatchPathValueComboDetector, NewMatchPathValueDetector, TimeCorrelationDetector, \
    TimestampsUnsortedDetector, Rules, WhitelistViolationDetector
from aminer.analysis.AtomFilters import MatchPathFilter, SubhandlerFilter, MatchValueFilter
from aminer.analysis.HistogramAnalysis import ModuloTimeBinDefinition, HistogramData, HistogramAnalysis
from aminer.analysis.TimeCorrelationViolationDetector import CorrelationRule, EventClassSelector, TimeCorrelationViolationDetector
from aminer.analysis.TimestampCorrectionFilters import SimpleMonotonicTimestampAdjust
from aminer.analysis.Rules import PathExistsMatchRule
from aminer.analysis.EnhancedNewMatchPathValueComboDetector import EnhancedNewMatchPathValueComboDetector
from aminer.analysis.NewMatchIdValueComboDetector import NewMatchIdValueComboDetector
from aminer.analysis.ParserCount import ParserCount
from aminer.analysis.EventCorrelationDetector import EventCorrelationDetector
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from aminer.input import LogAtom
from aminer.parsing import ParserMatch, MatchContext, MatchElement, DecimalIntegerValueModelElement, FirstMatchModelElement, \
    DelimitedDataModelElement, FixedWordlistDataModelElement, AnyByteDataModelElement, SequenceModelElement, FixedDataModelElement
from unit.TestBase import TestBase
import time
import random
from time import process_time
from _io import StringIO
import timeit


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
            new_match_path_detector = NewMatchPathDetector(self.aminer_config, [
                self.stream_printer_event_handler], 'Default', True)
            subhandler_filter = SubhandlerFilter([], stop_when_handled_flag=True)
            i = 0
            while i < number_of_pathes:
                match_path_filter = MatchPathFilter([(self.integerd + str(i), new_match_path_detector)], None)
                subhandler_filter.add_handler(match_path_filter, stop_when_handled_flag=True)
                i = i + 1
            t = round(time.time(), 3)

            # worst case
            decimal_integer_value_me = DecimalIntegerValueModelElement(
                'd' + str(number_of_pathes), DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                DecimalIntegerValueModelElement.PAD_TYPE_NONE)
            match_context = MatchContext(str(123456789).encode())
            match_element = decimal_integer_value_me.get_match_element('integer', match_context)
            log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, match_path_filter)
            worst_case = self.waiting_time / (timeit.timeit(lambda: subhandler_filter.receive_atom(log_atom), number=10000) / 10000)

            # best case
            decimal_integer_value_me = DecimalIntegerValueModelElement(
                'd' + str(0), DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                DecimalIntegerValueModelElement.PAD_TYPE_NONE)
            match_context = MatchContext(str(123456789).encode())
            match_element = decimal_integer_value_me.get_match_element('integer', match_context)
            log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, match_path_filter)
            best_case = self.waiting_time / (timeit.timeit(lambda: subhandler_filter.receive_atom(log_atom), number=10000) / 10000)

            results[z] = int((worst_case + best_case) / 2)
            z = z + 1
            avg = avg + (worst_case + best_case) / 2
        avg = int(avg / self.iterations)
        type(self).result = self.result + self.result_string % (
            subhandler_filter.__class__.__name__, avg, results, '%d different %ss with a %s.' % (
                number_of_pathes, match_path_filter.__class__.__name__, new_match_path_detector.__class__.__name__))

    def run_atom_filters_match_value_filter(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            new_match_path_detector = NewMatchPathDetector(self.aminer_config, [
                self.stream_printer_event_handler], 'Default', True)
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

            # worst case
            decimal_integer_value_me = DecimalIntegerValueModelElement(
                'd' + str(number_of_pathes), DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
            match_context = MatchContext(str(123456789).encode())
            match_element = decimal_integer_value_me.get_match_element('integer', match_context)
            log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, match_value_filter)
            worst_case = self.waiting_time / (timeit.timeit(lambda: subhandler_filter.receive_atom(log_atom), number=10000) / 10000)

            # best case
            decimal_integer_value_me = DecimalIntegerValueModelElement(
                'd' + str(0), DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
            match_context = MatchContext(str(123456789).encode())
            match_element = decimal_integer_value_me.get_match_element('integer', match_context)
            log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, match_value_filter)
            best_case = self.waiting_time / (timeit.timeit(lambda: subhandler_filter.receive_atom(log_atom), number=10000) / 10000)

            results[z] = int((worst_case + best_case) / 2)
            z = z + 1
            avg = avg + (worst_case + best_case) / 2
        avg = int(avg / self.iterations)
        type(self).result = self.result + self.result_string % (
            subhandler_filter.__class__.__name__, avg, results, '%d different %ss with a dictionary of %ss.' % (
                number_of_pathes, match_value_filter.__class__.__name__, new_match_path_detector.__class__.__name__))

    def run_new_match_path_detector(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            new_match_path_detector = NewMatchPathDetector(self.aminer_config, [
                self.stream_printer_event_handler], 'Default', True)
            t = round(time.time(), 3)
            measured_time = 0
            i = 0
            while measured_time < self.waiting_time / 10:
                decimal_integer_value_me = DecimalIntegerValueModelElement(
                    'd' + str(i % number_of_pathes), DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                    DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, new_match_path_detector)
                measured_time += timeit.timeit(lambda: new_match_path_detector.receive_atom(log_atom), number=1)
                i += 1

            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            new_match_path_detector.__class__.__name__, avg, results, self.different_pathes % number_of_pathes)

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
            enhanced_new_match_path_value_combo_detector = EnhancedNewMatchPathValueComboDetector(
                self.aminer_config, path_list, [self.stream_printer_event_handler], 'Default', True, True)
            t = round(time.time(), 3)

            # worst case
            decimal_integer_value_me = DecimalIntegerValueModelElement(
                'd' + str(number_of_pathes), DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                DecimalIntegerValueModelElement.PAD_TYPE_NONE)
            match_context = MatchContext(str(123456789).encode())
            match_element = decimal_integer_value_me.get_match_element('integer', match_context)
            log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, enhanced_new_match_path_value_combo_detector)
            worst_case = self.waiting_time / (
                    timeit.timeit(lambda: enhanced_new_match_path_value_combo_detector.receive_atom(log_atom), number=10000) / 10000)

            # best case
            decimal_integer_value_me = DecimalIntegerValueModelElement(
                'd' + str(0), DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
            match_context = MatchContext(str(123456789).encode())
            match_element = decimal_integer_value_me.get_match_element('integer', match_context)
            log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, enhanced_new_match_path_value_combo_detector)
            best_case = self.waiting_time / (
                    timeit.timeit(lambda: enhanced_new_match_path_value_combo_detector.receive_atom(log_atom), number=10000) / 10000)

            results[z] = int((worst_case + best_case) / 2)
            z = z + 1
            avg = avg + (worst_case + best_case) / 2
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
            histogram_analysis = HistogramAnalysis(
                self.aminer_config, [(histogram_data.property_path, modulo_time_bin_definition)], amplifier * self.waiting_time,
                [self.stream_printer_event_handler], False, 'Default')

            i = 0
            measured_time = 0
            t = time.time()
            while measured_time < self.waiting_time / 10:
                rand = random.randint(0, 100000)
                match_element = MatchElement('match/crontab', t + rand, t + rand, [])
                log_atom = LogAtom(histogram_data.bin_data, ParserMatch(match_element), t + i, histogram_analysis)
                measured_time += timeit.timeit(lambda: histogram_analysis.receive_atom(log_atom), number=1)
                i = i + 1
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            histogram_analysis.__class__.__name__, avg, results, '%d bin(s) and output after %d elements.' % (
                number_of_pathes, amplifier * self.waiting_time))

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
            t = time.time()
            match_value_average_change_detector = MatchValueAverageChangeDetector(self.aminer_config, [
                self.stream_printer_event_handler], None, path_list, 2, t, True, False, 'Default')
            i = 0
            while i < number_of_pathes:
                match_element = MatchElement(self.integerd + str(i), '%s' % str(t), t, [])
                log_atom = LogAtom(
                    match_element.get_match_object(), ParserMatch(match_element), t, match_value_average_change_detector)
                match_value_average_change_detector.receive_atom(log_atom)

                match_element = MatchElement(self.integerd + str(i), '%s' % str(t + 0.1), t + 0.1, [])
                log_atom = LogAtom(
                    match_element.get_match_object(), ParserMatch(match_element), t + 0.1, match_value_average_change_detector)
                match_value_average_change_detector.receive_atom(log_atom)

                match_element = MatchElement(self.integerd + str(i), '%s' % str(t + 0.2), t + 0.2, [])
                log_atom = LogAtom(
                    match_element.get_match_object(), ParserMatch(match_element), t + 0.2, match_value_average_change_detector)
                match_value_average_change_detector.receive_atom(log_atom)

                match_element = MatchElement(self.integerd + str(i), '%s' % str(t + 10), t + 10, [])
                log_atom = LogAtom(
                    match_element.get_match_object(), ParserMatch(match_element), t + 10, match_value_average_change_detector)
                match_value_average_change_detector.receive_atom(log_atom)
                i = i + 1
            t = time.time()

            # worst case
            match_element = MatchElement(self.integerd + str(number_of_pathes - 1), '%s' % str(t), t, [])
            log_atom = LogAtom(match_element.get_match_object(), ParserMatch(match_element), t, match_value_average_change_detector)
            worst_case = self.waiting_time / (
                    timeit.timeit(lambda: match_value_average_change_detector.receive_atom(log_atom), number=10000) / 10000)

            # best case
            match_element = MatchElement(self.integerd + str(0), '%s' % str(t), t, [])
            log_atom = LogAtom(match_element.get_match_object(), ParserMatch(match_element), t, match_value_average_change_detector)
            best_case = self.waiting_time / (
                    timeit.timeit(lambda: match_value_average_change_detector.receive_atom(log_atom), number=10000) / 10000)

            results[z] = int((worst_case + best_case) / 2)
            z = z + 1
            avg = avg + (worst_case + best_case) / 2
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            match_value_average_change_detector.__class__.__name__, avg, results, self.different_pathes % number_of_pathes)

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
                parsing_model.append(
                    DecimalIntegerValueModelElement('d' + str(i % number_of_pathes), DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                    DecimalIntegerValueModelElement.PAD_TYPE_NONE))
                parsing_model.append(FixedDataModelElement('s' + str(i % number_of_pathes), b' Euro '))
                i = i + 1
            sequence_model_element = SequenceModelElement('integer', parsing_model)
            match_value_stream_writer = MatchValueStreamWriter(self.output_stream, path_list, b';', b'-')
            t = time.time()

            data = b''
            for j in range(1, int(number_of_pathes / 2) + number_of_pathes % 2 + 1):
                data = data + str(j).encode() + b' Euro '
            match_context = MatchContext(data)
            match_element = sequence_model_element.get_match_element('match', match_context)
            log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, match_value_stream_writer)

            results[z] = int(self.waiting_time / (
                    timeit.timeit(lambda: match_value_stream_writer.receive_atom(log_atom), number=10000) / 10000))
            z = z + 1
            avg = avg + results[z - 1]
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            match_value_stream_writer.__class__.__name__, avg, results, self.different_pathes % number_of_pathes)

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
            missing_match_path_list_value_detector = MissingMatchPathListValueDetector(
                self.aminer_config, path_list, [self.stream_printer_event_handler], 'Default', True, 3600, 86400)
            t = time.time()

            # worst case
            decimal_integer_value_me = DecimalIntegerValueModelElement(
                'd' + str(number_of_pathes - 1), DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                DecimalIntegerValueModelElement.PAD_TYPE_NONE)
            match_context = MatchContext(str(1).encode())
            match_element = decimal_integer_value_me.get_match_element('integer', match_context)
            log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, missing_match_path_list_value_detector)
            worst_case = self.waiting_time / (
                    timeit.timeit(lambda: missing_match_path_list_value_detector.receive_atom(log_atom), number=10000) / 10000)

            # best case
            decimal_integer_value_me = DecimalIntegerValueModelElement(
                'd' + str(0), DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
            match_context = MatchContext(str(1).encode())
            match_element = decimal_integer_value_me.get_match_element('integer', match_context)
            log_atom = LogAtom(match_element.match_object, ParserMatch(match_element), t, missing_match_path_list_value_detector)
            best_case = self.waiting_time / (
                    timeit.timeit(lambda: missing_match_path_list_value_detector.receive_atom(log_atom), number=10000) / 10000)

            results[z] = (worst_case + best_case) / 2
            z = z + 1
            avg = avg + (worst_case + best_case) / 2
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            missing_match_path_list_value_detector.__class__.__name__, avg, results, self.different_pathes % number_of_pathes)

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
            new_match_path_value_combo_detector = NewMatchPathValueComboDetector(
                self.aminer_config, path_list, [self.stream_printer_event_handler], 'Default', True, True)
            t = time.time()
            measured_time = 0
            i = 0
            while measured_time < self.waiting_time / 10:
                decimal_integer_value_me = DecimalIntegerValueModelElement(
                    'd' + str(i % number_of_pathes), DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                    DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i % 100).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, new_match_path_value_combo_detector)
                measured_time += timeit.timeit(lambda: new_match_path_value_combo_detector.receive_atom(log_atom), number=1)
                i = i + 1
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            new_match_path_value_combo_detector.__class__.__name__, avg, results, self.different_attributes % number_of_pathes)

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
            new_match_path_value_detector = NewMatchPathValueDetector(self.aminer_config, path_list, [
                self.stream_printer_event_handler], 'Default', True, True)
            t = time.time()
            measured_time = 0
            i = 0
            while measured_time < self.waiting_time / 10:
                decimal_integer_value_me = DecimalIntegerValueModelElement(
                    'd' + str(i % number_of_pathes), DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                    DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i % 100).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, new_match_path_value_detector)
                measured_time += timeit.timeit(lambda: new_match_path_value_detector.receive_atom(log_atom), number=1)
                i = i + 1
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            new_match_path_value_detector.__class__.__name__, avg, results, self.different_attributes % number_of_pathes)

    def run_time_correlation_detector(self, number_of_rules):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            time_correlation_detector = TimeCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], number_of_rules,
                                                                'Default', self.waiting_time * 9000, True, True, True, 1, 5)
            t = time.time()
            measured_time = 0
            i = 0
            while measured_time < self.waiting_time / 10:
                decimal_integer_value_me = DecimalIntegerValueModelElement(
                    'd', DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i % 100).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, time_correlation_detector)
                measured_time += timeit.timeit(lambda: time_correlation_detector.receive_atom(log_atom), number=1)
                i = i + 1
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            time_correlation_detector.__class__.__name__, avg, results, 'test_count=%d.' % number_of_rules)

    def run_time_correlation_violation_detector(self, chance):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            correlation_rule = CorrelationRule('Correlation', 0, chance, max_artefacts_a_for_single_b=1,
                                               artefact_match_parameters=[('/integer/d0', '/integer/d1')])
            a_class_selector = EventClassSelector('Selector1', [correlation_rule], None)
            b_class_selector = EventClassSelector('Selector2', None, [correlation_rule])
            rules = [Rules.PathExistsMatchRule('/integer/d0', a_class_selector), Rules.PathExistsMatchRule('/integer/d1', b_class_selector)]

            time_correlation_violation_detector = TimeCorrelationViolationDetector(
                self.analysis_context.aminer_config, rules, [self.stream_printer_event_handler])
            s = time.time()
            measured_time = 0
            i = 0
            decimal_integer_value_me = DecimalIntegerValueModelElement(
                'd0', DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
            while measured_time < self.waiting_time / 10:
                integer = '/integer'
                r = random.randint(1, 100)
                decimal_integer_value_me1 = DecimalIntegerValueModelElement(
                    'd1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me.get_match_element(integer, match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), s, time_correlation_violation_detector)
                measured_time += timeit.timeit(lambda: time_correlation_violation_detector.receive_atom(log_atom), number=1)

                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me1.get_match_element(integer, match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), s + r / 100, time_correlation_violation_detector)
                measured_time += timeit.timeit(lambda: time_correlation_violation_detector.receive_atom(log_atom), number=1)
                s = s + r / 100

                if r / 100 >= chance:
                    match_context = MatchContext(str(i).encode())
                    match_element = decimal_integer_value_me.get_match_element(integer, match_context)
                    log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), s, time_correlation_violation_detector)
                    measured_time += timeit.timeit(lambda: time_correlation_violation_detector.receive_atom(log_atom), number=1)
                    i = i + 1
                time_correlation_violation_detector.do_timer(s)
                i = i + 2
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            time_correlation_violation_detector.__class__.__name__, avg, results,
            '%d%% chance of not finding an element' % ((1 - chance) * 100))

    def run_timestamp_correction_filters(self, number_of_pathes):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            new_match_path_detector = NewMatchPathDetector(self.aminer_config, [
                self.stream_printer_event_handler], 'Default', True)
            simple_monotonic_timestamp_adjust = SimpleMonotonicTimestampAdjust([new_match_path_detector])

            seconds = time.time()
            i = 0
            measured_time = 0
            while measured_time < self.waiting_time / 10:
                decimal_integer_value_me = DecimalIntegerValueModelElement(
                    'd' + str(i % number_of_pathes), DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                    DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                p = process_time()
                r = random.randint(1, 1000000)
                seconds = seconds + process_time() - p
                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), seconds - r, simple_monotonic_timestamp_adjust)
                measured_time += timeit.timeit(lambda: simple_monotonic_timestamp_adjust.receive_atom(log_atom), number=1)
                i = i + 1
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            simple_monotonic_timestamp_adjust.__class__.__name__, avg, results,
            'a %s and %d different path(es).' % (new_match_path_detector.__class__.__name__, number_of_pathes))

    def run_timestamps_unsorted_detector(self, reset_factor):
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            timestamps_unsorted_detector = TimestampsUnsortedDetector(self.aminer_config, [
                self.stream_printer_event_handler])
            s = time.time()
            i = 0
            measured_time = 0
            mini = 100
            while measured_time < self.waiting_time / 10:
                decimal_integer_value_me = DecimalIntegerValueModelElement(
                    'd', DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                r = random.randint(1, 100)
                match_context = MatchContext(str(i).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), s + min(r, mini), timestamps_unsorted_detector)
                measured_time += timeit.timeit(lambda: timestamps_unsorted_detector.receive_atom(log_atom), number=1)
                if mini > r:
                    mini = r
                else:
                    mini = mini + reset_factor
                i = i + 1
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            timestamps_unsorted_detector.__class__.__name__, avg, results, 'a reset_factor of %f.' % reset_factor)

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
            whitelist_violation_detector = WhitelistViolationDetector(self.aminer_config, rules, [self.stream_printer_event_handler])
            t = time.time()
            i = 0
            measured_time = 0
            while measured_time < self.waiting_time / 10:
                r = random.randint(1, 100)
                if r >= modulo_factor:
                    r = 2
                else:
                    r = 1
                decimal_integer_value_me = DecimalIntegerValueModelElement(
                    'd' + str(i % (number_of_pathes * r)), DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                    DecimalIntegerValueModelElement.PAD_TYPE_NONE)
                match_context = MatchContext(str(i % 100).encode())
                match_element = decimal_integer_value_me.get_match_element('integer', match_context)
                log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, whitelist_violation_detector)
                measured_time += timeit.timeit(lambda: whitelist_violation_detector.receive_atom(log_atom), number=1)
                i = i + 1
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            whitelist_violation_detector.__class__.__name__, avg, results,
            '%d different PathExistsMatchRules and a moduloFactor of %d.' % (number_of_pathes, modulo_factor))

    def run_new_match_id_value_combo_detector(self, min_allowed_time_diff):
        log_lines = [
            b'type=SYSCALL msg=audit(1580367384.000:1): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367385.000:1): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 '
            b'rdev=00:00 nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367386.000:2): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367387.000:2): item=0 name="two" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367388.000:3): arch=c000003e syscall=3 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367389.000:3): item=0 name="three" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00'
            b' nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367388.500:100): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=SYSCALL msg=audit(1580367390.000:4): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367391.000:4): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=PATH msg=audit(1580367392.000:5): item=0 name="two" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367393.000:5): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=SYSCALL msg=audit(1580367394.000:6): arch=c000003e syscall=4 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367395.000:7): item=0 name="five" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367396.000:8): arch=c000003e syscall=6 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367397.000:6): item=0 name="four" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367398.000:7): arch=c000003e syscall=5 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367399.000:8): item=0 name="six" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367400.000:9): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367401.000:9): item=0 name="three" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 '
            b'rdev=00:00 nametype=NORMAL',
            b'type=PATH msg=audit(1580367402.000:10): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 '
            b'rdev=00:00 nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367403.000:10): arch=c000003e syscall=3 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 '
            b'a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 '
            b'tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)']
        parsing_model = FirstMatchModelElement('type', [SequenceModelElement('path', [
            FixedDataModelElement('type', b'type=PATH '), FixedDataModelElement('msg_audit', b'msg=audit('),
            DelimitedDataModelElement('msg', b':'), FixedDataModelElement('placeholder', b':'),
            DecimalIntegerValueModelElement('id'), FixedDataModelElement('item_string', b'): item='),
            DecimalIntegerValueModelElement('item'), FixedDataModelElement('name_string', b' name="'),
            DelimitedDataModelElement('name', b'"'), FixedDataModelElement('inode_string', b'" inode='),
            DecimalIntegerValueModelElement('inode'), FixedDataModelElement('dev_string', b' dev='),
            DelimitedDataModelElement('dev', b' '), FixedDataModelElement('mode_string', b' mode='),
            DecimalIntegerValueModelElement('mode'), FixedDataModelElement('ouid_string', b' ouid='),
            DecimalIntegerValueModelElement('ouid'), FixedDataModelElement('ogid_string', b' ogid='),
            DecimalIntegerValueModelElement('ogid'), FixedDataModelElement('rdev_string', b' rdev='),
            DelimitedDataModelElement('rdev', b' '), FixedDataModelElement('nametype_string', b' nametype='),
            FixedWordlistDataModelElement('nametype', [b'NORMAL', b'ERROR'])]), SequenceModelElement('syscall', [
                FixedDataModelElement('type', b'type=SYSCALL '), FixedDataModelElement('msg_audit', b'msg=audit('),
                DelimitedDataModelElement('msg', b':'), FixedDataModelElement('placeholder', b':'),
                DecimalIntegerValueModelElement('id'), FixedDataModelElement('arch_string', b'): arch='),
                DelimitedDataModelElement('arch', b' '), FixedDataModelElement('syscall_string', b' syscall='),
                DecimalIntegerValueModelElement('syscall'), FixedDataModelElement('success_string', b' success='),
                FixedWordlistDataModelElement('success', [b'yes', b'no']),
                FixedDataModelElement('exit_string', b' exit='), DecimalIntegerValueModelElement('exit'),
                AnyByteDataModelElement('remainding_data')])])

        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            new_match_id_value_combo_detector = NewMatchIdValueComboDetector(self.aminer_config, [
                'parser/type/path/name', 'parser/type/syscall/syscall'], [self.stream_printer_event_handler],
                id_path_list=['parser/type/path/id', 'parser/type/syscall/id'], min_allowed_time_diff=min_allowed_time_diff,
                auto_include_flag=False, allow_missing_values_flag=True, persistence_id='audit_type_path', output_log_line=False)
            t = time.time()
            measured_time = 0
            i = 0
            while measured_time < self.waiting_time / 10:
                r = random.randint(0, len(log_lines)-1)
                line = log_lines[r]
                log_atom = LogAtom(
                    line, ParserMatch(parsing_model.get_match_element('parser', MatchContext(line))), t + i, self.__class__.__name__)
                measured_time += timeit.timeit(lambda: new_match_id_value_combo_detector.receive_atom(log_atom), number=1)
                i = i + 1
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            new_match_id_value_combo_detector.__class__.__name__, avg, results,
            '%.2f seconds min_allowed_time_diff.' % min_allowed_time_diff)

    def run_parser_count(self, set_target_path_list, report_after_number_of_elements):
        log_lines = [
            b'type=SYSCALL msg=audit(1580367384.000:1): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367385.000:1): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 '
            b'rdev=00:00 nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367386.000:2): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367387.000:2): item=0 name="two" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367388.000:3): arch=c000003e syscall=3 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367389.000:3): item=0 name="three" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00'
            b' nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367388.500:100): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=SYSCALL msg=audit(1580367390.000:4): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367391.000:4): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=PATH msg=audit(1580367392.000:5): item=0 name="two" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367393.000:5): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=SYSCALL msg=audit(1580367394.000:6): arch=c000003e syscall=4 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367395.000:7): item=0 name="five" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367396.000:8): arch=c000003e syscall=6 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367397.000:6): item=0 name="four" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367398.000:7): arch=c000003e syscall=5 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367399.000:8): item=0 name="six" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
            b'nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367400.000:9): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f '
            b'items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) '
            b'ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)',
            b'type=PATH msg=audit(1580367401.000:9): item=0 name="three" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 '
            b'rdev=00:00 nametype=NORMAL',
            b'type=PATH msg=audit(1580367402.000:10): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 '
            b'rdev=00:00 nametype=NORMAL',
            b'type=SYSCALL msg=audit(1580367403.000:10): arch=c000003e syscall=3 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 '
            b'a3=4f items=1 ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 '
            b'tty=(none) ses=4294967295 comm="apache2" exe="/usr/sbin/apache2" key=(null)']
        parsing_model = FirstMatchModelElement('type', [SequenceModelElement('path', [
            FixedDataModelElement('type', b'type=PATH '), FixedDataModelElement('msg_audit', b'msg=audit('),
            DelimitedDataModelElement('msg', b':'), FixedDataModelElement('placeholder', b':'),
            DecimalIntegerValueModelElement('id'), FixedDataModelElement('item_string', b'): item='),
            DecimalIntegerValueModelElement('item'), FixedDataModelElement('name_string', b' name="'),
            DelimitedDataModelElement('name', b'"'), FixedDataModelElement('inode_string', b'" inode='),
            DecimalIntegerValueModelElement('inode'), FixedDataModelElement('dev_string', b' dev='),
            DelimitedDataModelElement('dev', b' '), FixedDataModelElement('mode_string', b' mode='),
            DecimalIntegerValueModelElement('mode'), FixedDataModelElement('ouid_string', b' ouid='),
            DecimalIntegerValueModelElement('ouid'), FixedDataModelElement('ogid_string', b' ogid='),
            DecimalIntegerValueModelElement('ogid'), FixedDataModelElement('rdev_string', b' rdev='),
            DelimitedDataModelElement('rdev', b' '), FixedDataModelElement('nametype_string', b' nametype='),
            FixedWordlistDataModelElement('nametype', [b'NORMAL', b'ERROR'])]), SequenceModelElement('syscall', [
                FixedDataModelElement('type', b'type=SYSCALL '), FixedDataModelElement('msg_audit', b'msg=audit('),
                DelimitedDataModelElement('msg', b':'), FixedDataModelElement('placeholder', b':'),
                DecimalIntegerValueModelElement('id'), FixedDataModelElement('arch_string', b'): arch='),
                DelimitedDataModelElement('arch', b' '), FixedDataModelElement('syscall_string', b' syscall='),
                DecimalIntegerValueModelElement('syscall'), FixedDataModelElement('success_string', b' success='),
                FixedWordlistDataModelElement('success', [b'yes', b'no']),
                FixedDataModelElement('exit_string', b' exit='), DecimalIntegerValueModelElement('exit'),
                AnyByteDataModelElement('remainding_data')])])
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            if set_target_path_list:
                parser_count = ParserCount(self.aminer_config, ['parser/type/path/name', 'parser/type/syscall/syscall'], [
                    self.stream_printer_event_handler], report_after_number_of_elements, True)
            else:
                parser_count = ParserCount(self.aminer_config, None, [
                    self.stream_printer_event_handler], report_after_number_of_elements, True)
            t = time.time()
            measured_time = 0
            i = 0
            while measured_time < self.waiting_time / 10:
                r = random.randint(0, len(log_lines) - 1)
                line = log_lines[r]
                log_atom = LogAtom(line, ParserMatch(parsing_model.get_match_element('parser', MatchContext(line))), t + i,
                                   self.__class__.__name__)
                measured_time += timeit.timeit(lambda: parser_count.receive_atom(log_atom), number=1)
                i = i + 1
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            parser_count.__class__.__name__, avg, results,
            'set_target_path_list: %s, report_after_number_of_elements: %d' % (set_target_path_list, report_after_number_of_elements))

    def run_event_correlation_detector(self, generation, diff, p0, alpha, max_hypotheses, max_observations, candidates_size,
                                       hypothesis_eval_delta_time, delta_time_to_discard_hypothesis):
        alphabet = b'abcdefghijklmnopqrstuvwxyz'
        alphabet_model = FirstMatchModelElement('first', [])
        for i, char in enumerate(alphabet):
            char = bytes([char])
            alphabet_model.children.append(FixedDataModelElement(char.decode(), char))

        # training phase
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            ecd = EventCorrelationDetector(
                self.aminer_config, [self.stream_printer_event_handler], generation_factor=generation, generation_probability=generation,
                max_hypotheses=max_hypotheses, max_observations=max_observations, p0=p0, alpha=alpha, candidates_size=candidates_size,
                hypotheses_eval_delta_time=hypothesis_eval_delta_time, delta_time_to_discard_hypothesis=delta_time_to_discard_hypothesis)

            t = time.time()
            measured_time = 0
            i = 0
            while measured_time < self.waiting_time / 10:
                char = bytes([alphabet[i % len(alphabet)]])
                parser_match = ParserMatch(alphabet_model.get_match_element('parser', MatchContext(char)))
                t += diff
                measured_time += timeit.timeit(lambda: ecd.receive_atom(LogAtom(char, parser_match, t, self.__class__.__name__)), number=1)
                i = i + 1
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            ecd.__class__.__name__, avg, results,
            'auto_include_flag: %s, generation: %.2f, diff: %.2f, p0: %.2f, alpha: %.2f, max_hypothesis: %d, max_observations: %d, candid'
            'ates_size %d, hypothesis_eval_delta_time: %.2f, delta_time_to_discard_hypothesis: %.2f' % (
                ecd.auto_include_flag, generation, diff, p0, alpha, max_hypotheses, max_observations, candidates_size,
                hypothesis_eval_delta_time, delta_time_to_discard_hypothesis))

        # check_phase
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            ecd.auto_include_flag = False
            t = time.time()
            measured_time = 0
            i = 0
            while measured_time < self.waiting_time / 10:
                char = bytes([alphabet[i % len(alphabet)]])
                parser_match = ParserMatch(alphabet_model.get_match_element('parser', MatchContext(char)))
                t += diff
                measured_time += timeit.timeit(lambda: ecd.receive_atom(LogAtom(char, parser_match, t, self.__class__.__name__)), number=1)
                i = i + 1
            results[z] = i * 10
            z = z + 1
            avg = avg + i * 10
        avg = avg / self.iterations
        type(self).result = self.result + self.result_string % (
            ecd.__class__.__name__, avg, results,
            'auto_include_flag: %s, generation: %.2f, diff: %.2f, p0: %.2f, alpha: %.2f, max_hypothesis: %d, max_observations: %d, candid'
            'ates_size %d, hypothesis_eval_delta_time: %.2f, delta_time_to_discard_hypothesis: %.2f' % (
                ecd.auto_include_flag, generation, diff, p0, alpha, max_hypotheses, max_observations, candidates_size,
                hypothesis_eval_delta_time, delta_time_to_discard_hypothesis))

    def test01atom_filters(self):
        self.run_atom_filters_match_path_filter(1)
        self.run_atom_filters_match_path_filter(30)
        self.run_atom_filters_match_path_filter(100)

        self.run_atom_filters_match_value_filter(1)
        self.run_atom_filters_match_value_filter(30)
        self.run_atom_filters_match_value_filter(100)

    def test02enhanced_new_match_path_value_combo_detector(self):
        self.run_enhanced_new_match_path_value_combo_detector(1)
        self.run_enhanced_new_match_path_value_combo_detector(30)
        self.run_enhanced_new_match_path_value_combo_detector(100)

    def test03histogram_analysis(self):
        self.run_histogram_analysis(1, 100)
        self.run_histogram_analysis(30, 100)
        self.run_histogram_analysis(100, 100)
        self.run_histogram_analysis(10000, 100)

        self.run_histogram_analysis(1, 1000)
        self.run_histogram_analysis(30, 1000)
        self.run_histogram_analysis(100, 1000)
        self.run_histogram_analysis(10000, 1000)

        self.run_histogram_analysis(1, 10000)
        self.run_histogram_analysis(30, 10000)
        self.run_histogram_analysis(100, 10000)
        self.run_histogram_analysis(10000, 10000)

    def test04match_value_average_change_detector(self):
        self.run_match_value_average_change_detector(1)
        self.run_match_value_average_change_detector(30)
        self.run_match_value_average_change_detector(100)

    def test05match_value_stream_writer(self):
        self.run_match_value_stream_writer(1)
        self.run_match_value_stream_writer(30)
        self.run_match_value_stream_writer(100)

    def test06missing_match_path_value_detector(self):
        self.run_missing_match_path_value_detector(1)
        self.run_missing_match_path_value_detector(30)
        self.run_missing_match_path_value_detector(100)

    def test07new_match_path_detector(self):
        self.run_new_match_path_detector(1)
        self.run_new_match_path_detector(1000)
        self.run_new_match_path_detector(100000)

    def test08new_match_path_value_combo_detector(self):
        self.run_new_match_path_value_combo_detector(1)
        self.run_new_match_path_value_combo_detector(30)
        self.run_new_match_path_value_combo_detector(100)

    def test09new_match_path_value_detector(self):
        self.run_new_match_path_value_detector(1)
        self.run_new_match_path_value_detector(30)
        self.run_new_match_path_value_detector(100)

    def test10time_correlation_detector(self):
        self.run_time_correlation_detector(10)
        self.run_time_correlation_detector(100)
        self.run_time_correlation_detector(1000)

    def test11time_correlation_violation_detector(self):
        self.run_time_correlation_violation_detector(0.99)
        self.run_time_correlation_violation_detector(0.95)
        self.run_time_correlation_violation_detector(0.50)
        self.run_time_correlation_violation_detector(0.01)

    def test12timestamp_correction_filters(self):
        self.run_timestamp_correction_filters(1)
        self.run_timestamp_correction_filters(1000)
        self.run_timestamp_correction_filters(100000)

    def test13timestamps_unsorted_detector(self):
        self.run_timestamps_unsorted_detector(0.001)
        self.run_timestamps_unsorted_detector(0.1)
        self.run_timestamps_unsorted_detector(1)
        self.run_timestamps_unsorted_detector(100)

    def test14whitelist_violation_detector(self):
        self.run_whitelist_violation_detector(1, 99)
        self.run_whitelist_violation_detector(1, 50)
        self.run_whitelist_violation_detector(1, 1)
        self.run_whitelist_violation_detector(1000, 99)
        self.run_whitelist_violation_detector(1000, 50)
        self.run_whitelist_violation_detector(1000, 1)
        self.run_whitelist_violation_detector(100000, 99)
        self.run_whitelist_violation_detector(100000, 50)
        self.run_whitelist_violation_detector(100000, 1)

    def test15new_match_id_value_combo_detector(self):
        self.run_new_match_id_value_combo_detector(0.1)
        self.run_new_match_id_value_combo_detector(5)
        self.run_new_match_id_value_combo_detector(20)
        self.run_new_match_id_value_combo_detector(100)

    def test16parser_count(self):
        # use target_paths
        self.run_parser_count(True, 60)
        self.run_parser_count(True, 1000)
        self.run_parser_count(True, 10000)
        self.run_parser_count(True, 100000)

        # use no target_paths
        self.run_parser_count(False, 60)
        self.run_parser_count(False, 1000)
        self.run_parser_count(False, 10000)
        self.run_parser_count(False, 100000)

    def test17event_correlation_detector(self):
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(0.5, 5, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(0.1, 5, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 10, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 1, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 0.1, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 1.0, 0.01, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.7, 0.1, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 2000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 10000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 1000, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 2000, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 500, 10, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 500, 100, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 500, 5, 120, 180)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 500, 5, 60, 90)
        self.run_event_correlation_detector(1.0, 5, 0.9, 0.05, 1000, 500, 5, 30, 45)


if __name__ == '__main__':
    unittest.main()
