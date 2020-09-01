import unittest
import random
import time
from unit.TestBase import TestBase
from aminer.analysis.MatchFilter import MatchFilter
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
from aminer.input.LogAtom import LogAtom
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ParserMatch import ParserMatch
from datetime import datetime


class MatchFilterTest(TestBase):
    __expected_string = '%s Log Atom Filtered\nMatchFilter: "%s" (1 lines)\n  /integer: %d\n%d\n\n'

    def test1_receive_atom_trigger_event(self):
        """This test checks if an event is triggered if the path is in the target_path_list."""
        description = "Test1MatchFilterTest"
        decimal_integer_me = DecimalIntegerValueModelElement('integer')
        match_filter = MatchFilter(self.aminer_config, ['/integer'], [self.stream_printer_event_handler])
        self.analysis_context.register_component(match_filter, description)
        t = time.time()
        for i in range(1000):
            val = random.randint(0, 1000)
            log_atom = LogAtom(val, ParserMatch(decimal_integer_me.get_match_element('', MatchContext(str(val).encode('utf-8')))), t,
                               match_filter)
            match_filter.receive_atom(log_atom)
            self.assertEqual(self.__expected_string % (
                datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), description, val, val), self.output_stream.getvalue())
            self.reset_output_stream()

    def test2_receive_atom_trigger_no_event(self):
        """This test checks if an event is not triggered if the path is not in the target_path_list."""
        description = "Test2MatchFilterTest"
        decimal_integer_me = DecimalIntegerValueModelElement('integer')
        match_filter = MatchFilter(self.aminer_config, ['/strings'], [self.stream_printer_event_handler])
        self.analysis_context.register_component(match_filter, description)
        t = time.time()
        for i in range(1000):
            val = random.randint(0, 1000)
            log_atom = LogAtom(val, ParserMatch(decimal_integer_me.get_match_element('', MatchContext(str(val).encode('utf-8')))), t,
                               match_filter)
            match_filter.receive_atom(log_atom)
            self.assertEqual('', self.output_stream.getvalue())

    def test3_receive_atom_with_target_value(self):
        """This test checks if an event is triggered, when the path is in the target_path_list and the value is in the target_value_list."""
        description = "Test3MatchFilterTest"
        decimal_integer_me = DecimalIntegerValueModelElement('integer')
        match_filter = MatchFilter(self.aminer_config, ['/integer'], [self.stream_printer_event_handler], target_value_list=[
            i for i in range(1001)])
        self.analysis_context.register_component(match_filter, description)
        t = time.time()
        for i in range(1000):
            val = random.randint(0, 1000)
            log_atom = LogAtom(val, ParserMatch(decimal_integer_me.get_match_element('', MatchContext(str(val).encode('utf-8')))), t,
                               match_filter)
            match_filter.receive_atom(log_atom)
            self.assertEqual(self.__expected_string % (datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), description, val, val),
                             self.output_stream.getvalue())
            self.reset_output_stream()

    def test4_receive_atom_with_no_target_value(self):
        """This test checks if an event is not triggered, when the path is in the target_path_list and the value is not in the
        target_value_list."""
        description = "Test4MatchFilterTest"
        description = "Test3MatchFilterTest"
        decimal_integer_me = DecimalIntegerValueModelElement('integer')
        match_filter = MatchFilter(self.aminer_config, ['/integer'], [self.stream_printer_event_handler], target_value_list=[
            i for i in range(501)])
        self.analysis_context.register_component(match_filter, description)
        t = time.time()
        for i in range(1000):
            val = random.randint(0, 1000)
            log_atom = LogAtom(val, ParserMatch(decimal_integer_me.get_match_element('', MatchContext(str(val).encode('utf-8')))), t,
                               match_filter)
            match_filter.receive_atom(log_atom)
            if val <= 500:
                self.assertEqual(self.__expected_string % (datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), description, val, val),
                                 self.output_stream.getvalue())
            else:
                self.assertEqual('', self.output_stream.getvalue())
            self.reset_output_stream()


if __name__ == "__main__":
    unittest.main()
