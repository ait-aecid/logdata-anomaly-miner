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
        error_rate = 0.000085
        cls.perfect_data_diff5 = cls.generate_perfect_data(cls, 30000, 5)
        cls.perfect_data_diff1 = cls.generate_perfect_data(cls, 30000, 1)
        cls.errored_data_diff5 = cls.generate_errored_data(cls, 100000, 5, error_rate)
        cls.errored_data_diff1 = cls.generate_errored_data(cls, 100000, 1, error_rate)
        cls.errored_data_diff5_low_error_rate = cls.generate_errored_data(cls, 100000, 5, error_rate / 2.5)
        cls.errored_data_diff1_low_error_rate = cls.generate_errored_data(cls, 100000, 1, error_rate / 2.5)

    def test1learn_from_clear_examples(self):
        """In this test case perfect examples are used to learn and evaluate rules. The default parameters are used."""
        description = 'test1eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True)
        self.analysis_context.register_component(ecd, description)
        self.run_ecd_test(ecd, self.perfect_data_diff5[:12000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_ecd_test(ecd, self.perfect_data_diff1[:12000])

    def test2learn_from_clear_examples_with_smaller_probabilities(self):
        """Like in test1 perfect examples are used, but the generation_probability and generation_factor are set to 0.5 in the first case
        and 0.1 in the second case. The EventCorrelationDetector should still learn the rules as expected."""
        description = 'test2eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.5, generation_factor=0.5)
        self.analysis_context.register_component(ecd, description)
        self.run_ecd_test(ecd, self.perfect_data_diff5[:30000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.5, generation_factor=0.5)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_ecd_test(ecd, self.perfect_data_diff1[:30000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.3, generation_factor=0.3)
        self.analysis_context.register_component(ecd, description + '3')
        self.run_ecd_test(ecd, self.perfect_data_diff5[:100000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.3, generation_factor=0.3)
        self.analysis_context.register_component(ecd, description + '4')
        self.run_ecd_test(ecd, self.perfect_data_diff1[:100000])

    def test3learn_from_examples_with_errors(self):
        """In this test case examples with errors are used, but still should be learned. The same parameters like in test1 are used."""
        description = 'test3eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True)
        self.analysis_context.register_component(ecd, description)
        self.run_ecd_test(ecd, self.errored_data_diff5[:12000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_ecd_test(ecd, self.errored_data_diff1[:12000])

    def test4learn_from_examples_with_errors_and_smaller_probabilities(self):
        """In this test case examples with errors are used, but still should be learned. These tests are using a higher
        generation_probability and generation_factor, because the data contains errors."""
        description = 'test4eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.7, generation_factor=0.99)
        self.analysis_context.register_component(ecd, description)
        self.run_ecd_test(ecd, self.errored_data_diff5_low_error_rate[:25000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.7, generation_factor=0.99)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_ecd_test(ecd, self.errored_data_diff1_low_error_rate[:25000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.5, generation_factor=0.95)
        self.analysis_context.register_component(ecd, description + '3')
        self.run_ecd_test(ecd, self.errored_data_diff5_low_error_rate[:40000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True,
                                       generation_probability=0.5, generation_factor=0.95)
        self.analysis_context.register_component(ecd, description + '4')
        self.run_ecd_test(ecd, self.errored_data_diff1_low_error_rate[:40000])

    def test5learn_safe_assumptions(self):
        """In this test case p0 and alpha are chosen carefully to only find safe assumptions about the implications in the data. Therefor
        more iterations in the training phase are needed."""
        description = 'test5eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01)
        self.analysis_context.register_component(ecd, description)
        self.run_ecd_test(ecd, self.perfect_data_diff5[:20000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_ecd_test(ecd, self.errored_data_diff5_low_error_rate[:40000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01)
        self.analysis_context.register_component(ecd, description + '3')
        self.run_ecd_test(ecd, self.perfect_data_diff1[:20000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=1.0, alpha=0.01)
        self.analysis_context.register_component(ecd, description + '4')
        self.run_ecd_test(ecd, self.errored_data_diff1_low_error_rate[:40000])

    def test6approximately_learn_implications(self):
        """In this unittest p0 and alpha are chosen to approximately find sequences in log data. Therefor not as many iterations are needed
        to learn the rules."""
        description = 'test6eventCorrelationDetectorTest'
        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1)
        self.analysis_context.register_component(ecd, description)
        self.run_ecd_test(ecd, self.perfect_data_diff5[:10000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1)
        self.analysis_context.register_component(ecd, description + '2')
        self.run_ecd_test(ecd, self.errored_data_diff5[:10000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1)
        self.analysis_context.register_component(ecd, description + '3')
        self.run_ecd_test(ecd, self.perfect_data_diff1[:10000])

        ecd = EventCorrelationDetector(self.aminer_config, [self.stream_printer_event_handler], check_rules_flag=True, p0=0.7, alpha=0.1)
        self.analysis_context.register_component(ecd, description + '4')
        self.run_ecd_test(ecd, self.errored_data_diff1[:10000])

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

    def run_ecd_test(self, ecd, log_atoms):
        diff = log_atoms[1].atom_time - log_atoms[0].atom_time
        for log_atom in log_atoms:
            ecd.receive_atom(log_atom)
        sorted_forward_rules = dict(sorted(ecd.forward_rules.items()))
        sorted_back_rules = dict(sorted(ecd.back_rules.items()))
        self.assertEqual(len(sorted_forward_rules), len(self.alphabet_model.children))
        self.assertEqual(len(sorted_back_rules), len(self.alphabet_model.children))
        self.check_rules(sorted_back_rules, sorted_forward_rules, diff)
        ecd.auto_include_flag = False
        self.check_anomaly_detection(ecd, log_atom.atom_time, diff)

    def generate_perfect_data(self, iterations, diff):
        log_atoms = []
        t = time()
        for i in range(1, iterations+1):
            char = bytes([self.alphabet[i % len(self.alphabet)]])
            parser_match = ParserMatch(self.alphabet_model.get_match_element('parser', MatchContext(char)))
            t += diff
            log_atoms.append(LogAtom(char, parser_match, t, self.__class__.__name__))
        return log_atoms

    def generate_errored_data(self, iterations, diff, error_rate):
        log_atoms = []
        t = time()
        divisor = 1
        while error_rate * divisor < 1:
            divisor = divisor * 10
        err = divisor * error_rate
        divisor //= err
        for i in range(1, iterations+1):
            if i % divisor == 0 and i != 0:
                char = bytes([self.alphabet[int(i + random.uniform(diff+1, len(self.alphabet))) % len(self.alphabet)]])
            else:
                char = bytes([self.alphabet[i % len(self.alphabet)]])
            parser_match = ParserMatch(self.alphabet_model.get_match_element('parser', MatchContext(char)))
            t += diff
            log_atoms.append(LogAtom(char, parser_match, t, self.__class__.__name__))
        return log_atoms


if __name__ == "__main__":
    unittest.main()
