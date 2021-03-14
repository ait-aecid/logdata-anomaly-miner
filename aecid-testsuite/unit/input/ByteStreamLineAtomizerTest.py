import unittest
from aminer.input.ByteStreamLineAtomizer import ByteStreamLineAtomizer
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
import sys
from unit.TestBase import TestBase


class ByteStreamLineAtomizerTest(TestBase):
    """Unittests for the ByteStreamLineAtomizer."""

    illegal_access1 = b'WARNING: All illegal access operations will be denied in a future release'
    illegal_access2 = 'WARNING: All illegal access operations will be denied in a future release\n\n'

    def test1normal_line(self):
        """A normal line is tested as Input of the Class."""
        any_dme = AnyByteDataModelElement('s')
        byte_stream_line_atomizer = ByteStreamLineAtomizer(any_dme, [], [self.stream_printer_event_handler], 300, [])
        data = self.illegal_access1 + b'\n'
        self.assertEqual(byte_stream_line_atomizer.consume_data(data, False), len(data))

    def test2normal_complete_overlong_line(self):
        """A complete, overlong line is tested as Input of the Class."""
        match_context_fixed_dme = MatchContext(self.illegal_access1)
        any_dme = AnyByteDataModelElement('s')
        _match_element_fixed_dme = any_dme.get_match_element("match1", match_context_fixed_dme)

        byte_stream_line_atomizer = ByteStreamLineAtomizer(
            any_dme, [], [self.stream_printer_event_handler], sys.getsizeof(match_context_fixed_dme.match_data) - 1, [])
        self.assertGreater(
            byte_stream_line_atomizer.consume_data(self.illegal_access1 + b'\n', False), 0)
        self.assertEqual(self.output_stream.getvalue(), 'Overlong line detected (1 lines)\n  %s' % self.illegal_access2)

    def test3normal_incomplete_overlong_line_stream_not_ended(self):
        """A incomplete, overlong line, with the stream NOT ended, is tested as Input of the Class."""
        match_context_fixed_dme = MatchContext(self.illegal_access1)
        any_dme = AnyByteDataModelElement('s')
        _match_element_fixed_dme = any_dme.get_match_element("match1", match_context_fixed_dme)

        byte_stream_line_atomizer = ByteStreamLineAtomizer(
            any_dme, [], [self.stream_printer_event_handler], sys.getsizeof(match_context_fixed_dme.match_data) - 1, [])
        self.assertGreater(byte_stream_line_atomizer.consume_data(self.illegal_access1, False), 0)
        self.assertEqual(self.output_stream.getvalue(), 'Start of overlong line detected (1 lines)\n  %s' % self.illegal_access2)

    def test4normal_incomplete_overlong_line_stream_ended(self):
        """A incomplete, overlong line, with the stream ended, is tested as Input of the Class."""
        any_dme = AnyByteDataModelElement('s')
        byte_stream_line_atomizer = ByteStreamLineAtomizer(any_dme, [], [self.stream_printer_event_handler], 300, [])
        self.assertGreater(byte_stream_line_atomizer.consume_data(self.illegal_access1, True), 0)
        self.assertEqual(self.output_stream.getvalue(), 'Incomplete last line (1 lines)\n  %s' % self.illegal_access2)

    def test5eol_sep(self):
        """Test the eol_sep parameter."""
        searched = b'WARNING: All illegal access operations will be denied in a future release\nAnother line of data\nThe third line of ' \
                   b'data.'
        any_dme = AnyByteDataModelElement('s')
        byte_stream_line_atomizer = ByteStreamLineAtomizer(any_dme, [], [self.stream_printer_event_handler], 300, [], eol_sep=b'\n\n')
        data = searched + b'\n\nother line'
        self.assertEqual(byte_stream_line_atomizer.consume_data(data, False), len(data)-len(b'other line'))

    def test6json_format(self):
        """Check if json formatted log data can be processed with the json_format flag."""
        json_data = b'{\n\t"a": 1,\n\t"b": {"x": 2}}'
        data = b'some log line.'
        any_dme = AnyByteDataModelElement('s')
        byte_stream_line_atomizer = ByteStreamLineAtomizer(any_dme, [], [self.stream_printer_event_handler], 300, [], json_format=True)
        self.assertEqual(byte_stream_line_atomizer.consume_data(json_data + data, False), len(json_data))

        # this is no valid json and should process only data until the last \n
        self.assertEqual(byte_stream_line_atomizer.consume_data(data + json_data + data, False), len(data) + json_data.rfind(b'\n') + 1)

        json_data = b'{"a": 1, "b": {"c": 2}, "d": 3}\n{"a": 1, "b": {"c": 2}, "d": 3}'
        self.assertEqual(byte_stream_line_atomizer.consume_data(json_data, False), len(json_data))
        self.assertEqual(byte_stream_line_atomizer.consume_data(json_data + data, False), len(json_data))

        json_data = b'{\n\t"a": 1,\n\t"b": {\n\t\t"c": 2},\n\t"d": 3}{\n"a": 1,\n\t"b": {\n\t\t"c": 2},\n\t"d": 3}'
        self.assertEqual(byte_stream_line_atomizer.consume_data(json_data + data, False), len(json_data))
        self.assertEqual(byte_stream_line_atomizer.consume_data(data + json_data, False), len(data) + json_data.rfind(b'\n') + 1)

        # even when the first json data gets invalidated, the second one starts after an empty line and is therefore valid until the end.
        json_data = b'{\n\t"a": 1,\n\t"b": {\n\t\t"c": 2},\n\t"d": 3}\n\n{\n"a": 1,\n\t"b": {\n\t\t"c": 2},\n\t"d": 3}'
        self.assertEqual(byte_stream_line_atomizer.consume_data(json_data + data, False), len(json_data))
        self.assertEqual(byte_stream_line_atomizer.consume_data(data + json_data + data, False), len(data) + len(json_data))

        # this is an incomplete json, but it still can be valid.
        json_data = b'{"a": 1, "b": {"c": 2}, "d": 3}\n{"a": 1, "b": {"c": 2}, "d'
        self.assertEqual(byte_stream_line_atomizer.consume_data(json_data, False), json_data.rfind(b'\n') + 1)

        # this is an incomplete json and the end can not be valid.
        json_data = b'{"a": 1, "b": {"c": 2}, "d": 3}\n{"a": 1, "b": {"c": 2}, d'
        self.assertEqual(byte_stream_line_atomizer.consume_data(json_data, False), json_data.rfind(b'\n') + 1)

    def test7json_max_line_length(self):
        """Check if json data is not parsed over the max_line_length."""
        json_data = b'{\n\t"a": 1,\n\t"b": {\n\t\t"c": 2},\n\t"d": 3}\n{\n"a": 1,\n\t"b": {"c": 2},"d": 3}\n'
        single_line_json_data = b'{"a": 1,"b": {"c": 2},"d": 3}{"a": 1,"b": {"c": 2},"d": 3'
        any_dme = AnyByteDataModelElement('s')
        byte_stream_line_atomizer = ByteStreamLineAtomizer(any_dme, [], [self.stream_printer_event_handler], 25, [], json_format=True)
        self.assertEqual(byte_stream_line_atomizer.consume_data(json_data, False), json_data.rfind(b'\n') + 1)
        self.assertEqual(self.output_stream.getvalue(), '')
        self.assertEqual(byte_stream_line_atomizer.consume_data(json_data, True), len(json_data))
        self.assertEqual(self.output_stream.getvalue(), '')
        byte_stream_line_atomizer = ByteStreamLineAtomizer(any_dme, [], [self.stream_printer_event_handler], 100, [], json_format=True)
        self.assertEqual(byte_stream_line_atomizer.consume_data(json_data, False), len(json_data))
        self.assertEqual(self.output_stream.getvalue(), '')
        self.assertEqual(byte_stream_line_atomizer.consume_data(json_data, True), len(json_data))
        self.assertEqual(self.output_stream.getvalue(), '')

        byte_stream_line_atomizer = ByteStreamLineAtomizer(any_dme, [], [self.stream_printer_event_handler], 25, [], json_format=True)
        self.assertEqual(byte_stream_line_atomizer.consume_data(single_line_json_data, True), len(single_line_json_data))
        self.assertEqual(self.output_stream.getvalue(), 'Overlong line terminated by end of stream (1 lines)\n  {"a": 1,"b": {"c": 2},"d":'
                                                        ' 3}{"a": 1,"b": {"c": 2},"d": 3\n\n')
        self.reset_output_stream()
        self.assertEqual(byte_stream_line_atomizer.consume_data(single_line_json_data, False), len(single_line_json_data))
        self.assertEqual(self.output_stream.getvalue(), '')
        byte_stream_line_atomizer = ByteStreamLineAtomizer(any_dme, [], [self.stream_printer_event_handler], 100, [], json_format=True)
        self.assertEqual(byte_stream_line_atomizer.consume_data(single_line_json_data, True), len(single_line_json_data))
        self.assertEqual(self.output_stream.getvalue(), 'Incomplete last line (1 lines)\n  {"a": 1,"b": {"c": 2},"d": 3\n\n')
        self.reset_output_stream()
        self.assertEqual(byte_stream_line_atomizer.consume_data(single_line_json_data, False), len(
            single_line_json_data.rsplit(b'}', 2)[0]) + 1)
        self.assertEqual(self.output_stream.getvalue(), '')


if __name__ == "__main__":
    unittest.main()
