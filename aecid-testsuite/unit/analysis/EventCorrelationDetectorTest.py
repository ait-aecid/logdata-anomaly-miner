import unittest
from aminer.analysis.EventCorrelationDetector import EventCorrelationDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ParserMatch import ParserMatch
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from unit.TestBase import TestBase
from time import time
import random


class EventCorrelationDetectorTest(TestBase):
    alphabet = b'abcdefghijklmnopqrstuvwxyz'
    alphabet_model = FirstMatchModelElement('first', [])

    @classmethod
    def setUpClass(cls):
        for i in range(len(cls.alphabet)):
            char = bytes([cls.alphabet[i]])
            cls.alphabet_model.children.append(FixedDataModelElement(char.decode(), char))

    def test1learn_from_clear_examples(self):
        """In this test case perfect examples are used to learn and evaluate rules. The default parameters are used with exception to the
        candidates_size being 1 and 10."""
        description = 'test1eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True)
        self.analysis_context.register_component(ecd, description)
        self.run_perfect_ecd_test(ecd, 5, 12012)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_perfect_ecd_test(ecd, 1, 60060)

    def test2learn_from_clear_examples_with_smaller_probabilities(self):
        """Like in test1 perfect examples are used, but the generation_probability and generation_factor are set to 0.5 in the first case
        and 0.1 in the second case. The EventCorrelationDetector should still learn the rules as expected. The candidates_size is like in
        test1 1 and 10."""
        description = 'test2eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.5, generation_factor=0.5)
        self.analysis_context.register_component(ecd, description)
        self.run_perfect_ecd_test(ecd, 5, 15002)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.5, generation_factor=0.5)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_perfect_ecd_test(ecd, 1, 60060)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.1, generation_factor=0.1)
        self.analysis_context.register_component(ecd, description + '3')
        self.run_perfect_ecd_test(ecd, 5, 60060)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.1, generation_factor=0.1)
        self.analysis_context.register_component(ecd, description + '4')
        self.run_perfect_ecd_test(ecd, 1, 120120)

    def test3learn_from_examples_with_errors(self):
        """In this test case examples with errors are used, but still should be learned. The same parameters like in test1 are used."""
        description = 'test3eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True)
        self.analysis_context.register_component(ecd, description)
        self.run_errored_ecd_test(ecd, 5, 15002, error_rate=0.00001)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_errored_ecd_test(ecd, 1, 144144, error_rate=0.000001)

    def test4learn_from_examples_with_errors_and_smaller_probabilities(self):
        """In this test case examples with errors are used, but still should be learned. The same parameters like in test2 are used."""
        description = 'test4eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.5, generation_factor=0.5)
        self.analysis_context.register_component(ecd, description)
        self.run_errored_ecd_test(ecd, 5, 15002, error_rate=0.00001)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.5, generation_factor=0.5)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_errored_ecd_test(ecd, 1, 84084, error_rate=0.00001)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.1, generation_factor=0.1)
        self.analysis_context.register_component(ecd, description + '3')
        self.run_errored_ecd_test(ecd, 5, 60060, error_rate=0.00004)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.1, generation_factor=0.1)
        self.analysis_context.register_component(ecd, description + '4')
        self.run_errored_ecd_test(ecd, 1, 120120, error_rate=0.000001)

    def test5learn_safe_assumptions(self):
        """In this test case p0 and alpha are chosen carefully to only find safe assumptions about the implications in the data. Therefor
        more iterations in the training phase are needed."""
        description = 'test5eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01)
        self.analysis_context.register_component(ecd, description)
        self.run_perfect_ecd_test(ecd, 5, 15002)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_errored_ecd_test(ecd, 5, 60060, error_rate=0.00001)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01)
        self.analysis_context.register_component(ecd, description + '3')
        self.run_perfect_ecd_test(ecd, 1, 72072)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01)
        self.analysis_context.register_component(ecd, description + '4')
        self.run_errored_ecd_test(ecd, 1, 100022, error_rate=0.00001)

    def test6approximately_learn_implications(self):
        """In this unittest p0 and alpha are chosen to approximately find sequences in log data. Therefor not as many iterations are needed
        to learn the rules."""
        description = 'test6eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1)
        self.analysis_context.register_component(ecd, description)
        self.run_perfect_ecd_test(ecd, 5, 10010)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_errored_ecd_test(ecd, 5, 12012, error_rate=0.0001)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1)
        self.analysis_context.register_component(ecd, description + '3')
        self.run_perfect_ecd_test(ecd, 1, 48048)

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1)
        self.analysis_context.register_component(ecd, description + '4')
        self.run_errored_ecd_test(ecd, 1, 48048, error_rate=0.00001)

    def check_rules(self, sorted_back_rules, sorted_forward_rules, diff):
        for path in sorted_forward_rules:
            self.assertEqual(len(sorted_forward_rules[path]), 5 / diff)
            implications = []
            trigger = b''
            for rule in sorted_forward_rules[path]:
                trigger = rule.trigger_event[0].split('/')[-1].encode()
                implications.append(self.alphabet.index(rule.implied_event[0].split('/')[-1].encode()))
            for i in range(1, len(sorted_forward_rules[path]), 1):
                self.assertIn((self.alphabet.index(trigger) + i) % len(self.alphabet), implications)
        for path in sorted_back_rules:
            self.assertEqual(len(sorted_back_rules[path]), 5 / diff)
            trigger = b''
            implications = []
            for rule in sorted_back_rules[path]:
                trigger = rule.trigger_event[0].split('/')[-1].encode()
                implications.append(self.alphabet.index(rule.implied_event[0].split('/')[-1].encode()))
            for i in range(1, len(sorted_back_rules[path]), 1):
                self.assertIn((self.alphabet.index(trigger) - i) % len(self.alphabet), implications)

    def check_anomaly_detection(self, ecd, t, diff):
        for char in self.alphabet:
            self.reset_output_stream()
            char = bytes([char])
            parser_match = ParserMatch(self.alphabet_model.get_match_element('parser', MatchContext(char)))
            t += 5 * 3
            ecd.receive_atom(LogAtom(char, parser_match, t, self.__class__.__name__))
            # another LogAtom must be received to check the follow anomalies.
            t += 5 * 3
            ecd.receive_atom(LogAtom(char, parser_match, t, self.__class__.__name__))
            # print(self.output_stream.getvalue())

            # precede anomaly
            for i in range(1, int(5 / diff) + 1, 1):
                # print("in")
                # print(bytes([self.alphabet[(self.alphabet.index(char) - i) % len(self.alphabet)]]))
                self.assertIn('Event %s is missing, but should precede event %s' % (
                    bytes([self.alphabet[(self.alphabet.index(char) - i) % len(self.alphabet)]]), char), self.output_stream.getvalue())
            for i in range(int(5 / diff) + 1, len(self.alphabet), 1):
                # print("not in")
                # print(bytes([self.alphabet[(self.alphabet.index(char) - i) % len(self.alphabet)]]))
                self.assertNotIn('Event %s is missing, but should precede event %s' % (
                    bytes([self.alphabet[(self.alphabet.index(char) - i) % len(self.alphabet)]]), char), self.output_stream.getvalue())

            # follow anomaly
            for i in range(1, int(5 / diff) + 1, 1):
                # print("in")
                # print(bytes([self.alphabet[(self.alphabet.index(char) + i) % len(self.alphabet)]]))
                self.assertIn('Event %s is missing, but should follow event %s' % (
                    bytes([self.alphabet[(self.alphabet.index(char) + i) % len(self.alphabet)]]), char), self.output_stream.getvalue())
            for i in range(int(5 / diff) + 1, len(self.alphabet), 1):
                # print("not in")
                # print(bytes([self.alphabet[(self.alphabet.index(char) + i) % len(self.alphabet)]]))
                self.assertNotIn('Event %s is missing, but should follow event %s' % (
                    bytes([self.alphabet[(self.alphabet.index(char) + i) % len(self.alphabet)]]), char), self.output_stream.getvalue())

    def run_perfect_ecd_test(self, ecd, diff, iterations):
        t = time()
        for i in range(iterations):
            char = bytes([self.alphabet[i % len(self.alphabet)]])
            parser_match = ParserMatch(self.alphabet_model.get_match_element('parser', MatchContext(char)))
            t += diff
            ecd.receive_atom(LogAtom(char, parser_match, t, self.__class__.__name__))
        sorted_forward_rules = dict(sorted(ecd.forward_rules.items()))
        sorted_back_rules = dict(sorted(ecd.back_rules.items()))
        self.assertEqual(len(sorted_forward_rules), len(self.alphabet_model.children))
        self.assertEqual(len(sorted_back_rules), len(self.alphabet_model.children))
        self.check_rules(sorted_back_rules, sorted_forward_rules, diff)
        ecd.auto_include_flag = False
        self.check_anomaly_detection(ecd, t, diff)

    def run_errored_ecd_test(self, ecd, diff, iterations, error_rate):
        t = time()
        divisor = 1
        while error_rate * divisor < 1:
            divisor = divisor * 10
        err = divisor * error_rate
        for i in range(iterations):
            if i % divisor < err and i != 0:
                char = bytes([self.alphabet[(i + random.randint(5, len(self.alphabet))) % len(self.alphabet)]])
            else:
                char = bytes([self.alphabet[i % len(self.alphabet)]])
            parser_match = ParserMatch(self.alphabet_model.get_match_element('parser', MatchContext(char)))
            t += diff
            ecd.receive_atom(LogAtom(char, parser_match, t, self.__class__.__name__))
        sorted_forward_rules = dict(sorted(ecd.forward_rules.items()))
        sorted_back_rules = dict(sorted(ecd.back_rules.items()))
        self.assertEqual(len(sorted_forward_rules), len(self.alphabet_model.children))
        self.assertEqual(len(sorted_back_rules), len(self.alphabet_model.children))
        self.check_rules(sorted_back_rules, sorted_forward_rules, diff)
        ecd.auto_include_flag = False
        self.check_anomaly_detection(ecd, t, diff)


if __name__ == "__main__":
    unittest.main()
