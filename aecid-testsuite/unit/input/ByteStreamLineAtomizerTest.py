import unittest
from aminer.input.ByteStreamLineAtomizer import ByteStreamLineAtomizer
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
import sys
from unit.TestBase import TestBase


class ByteStreamLineAtomizerTest(TestBase):
    illegal_access1 = b'WARNING: All illegal access operations will be denied in a future release'
    illegal_access2 = 'WARNING: All illegal access operations will be denied in a future release\n\n'

    def test1normal_line(self):
        """A normal line is tested as Input of the Class."""
        fixed_dme = FixedDataModelElement('s1', self.illegal_access1)
        byte_stream_line_atomizer = ByteStreamLineAtomizer(fixed_dme, [], [self.stream_printer_event_handler], 300, [])
        self.assertGreater(
            byte_stream_line_atomizer.consume_data(b'WARNING: All illegal access operations will be denied in a future release\n', True), 0)

    def test2normal_complete_overlong_line(self):
        """A complete, overlong line is tested as Input of the Class."""
        match_context_fixed_dme = MatchContext(self.illegal_access1)
        fixed_dme = FixedDataModelElement('s1', self.illegal_access1)
        _match_element_fixed_dme = fixed_dme.get_match_element("match1", match_context_fixed_dme)

        byte_stream_line_atomizer = ByteStreamLineAtomizer(
            fixed_dme, [], [self.stream_printer_event_handler], sys.getsizeof(match_context_fixed_dme.match_data) - 1, [])
        self.assertGreater(
            byte_stream_line_atomizer.consume_data(b'WARNING: All illegal access operations will be denied in a future release\n', True), 0)
        self.assertEqual(self.output_stream.getvalue(), 'Overlong line detected (1 lines)\n  %s' % self.illegal_access2)

    def test3normal_incomplete_overlong_line_stream_not_ended(self):
        """A incomplete, overlong line, with the stream NOT ended, is tested as Input of the Class."""
        match_context_fixed_dme = MatchContext(self.illegal_access1)
        fixed_dme = FixedDataModelElement('s1', self.illegal_access1)
        _match_element_fixed_dme = fixed_dme.get_match_element("match1", match_context_fixed_dme)

        byte_stream_line_atomizer = ByteStreamLineAtomizer(
            fixed_dme, [], [self.stream_printer_event_handler], sys.getsizeof(match_context_fixed_dme.match_data) - 1, [])
        self.assertGreater(byte_stream_line_atomizer.consume_data(self.illegal_access1, False), 0)
        self.assertEqual(self.output_stream.getvalue(), 'Start of overlong line detected (1 lines)\n  %s' % self.illegal_access2)

    def test4normal_incomplete_overlong_line_stream_ended(self):
        """A incomplete, overlong line, with the stream ended, is tested as Input of the Class."""
        fixed_dme = FixedDataModelElement('s1', self.illegal_access1)
        byte_stream_line_atomizer = ByteStreamLineAtomizer(fixed_dme, [], [self.stream_printer_event_handler], 300, [])
        self.assertGreater(byte_stream_line_atomizer.consume_data(self.illegal_access1, True), 0)
        self.assertEqual(self.output_stream.getvalue(), 'Incomplete last line (1 lines)\n  %s' % self.illegal_access2)


if __name__ == "__main__":
    unittest.main()
