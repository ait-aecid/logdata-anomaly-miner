import unittest
from aminer.input.ByteStreamLineAtomizer import ByteStreamLineAtomizer
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.analysis import AtomFilters
from aminer.analysis.UnparsedAtomHandlers import SimpleUnparsedAtomHandler
from aminer.parsing.XmlModelElement import XmlModelElement
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
import sys
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyNumberModelElement


class ByteStreamLineAtomizerTest(TestBase):
    """Unittests for the ByteStreamLineAtomizer."""

    def test1consume_data(self):
        """
        Test the main functionality of the ByteStreamLineAtomizer by running the consume_data method.
        All other methods are called by the consume_data method and are not meant to be private methods of the class.
        """
        data = b"fixed data"
        overlong = "Overlong line detected (1 lines)\n  fixed data\n\n"
        start_overlong = "Start of overlong line detected (1 lines)\n  fixed data\n\n"
        overlong_end = "Overlong line terminated by end of stream (1 lines)\n  fixed data\n\n"
        output = "New path(s) detected\nNewMatchPathDetector: \"None\" (1 lines)\n  ['/fixed']\n\n"
        unparsed = "Unparsed atom received\nSimpleUnparsedAtomHandler: \"None\" (1 lines)\n   no match\n\n"
        incomplete = "Incomplete last line (1 lines)\n  fixed data\n\n"
        fdme = DummyFixedDataModelElement("fixed", data)
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=False, output_logline=False)
        atom_filter = AtomFilters.SubhandlerFilter(None)

        simple_unparsed_atom_handler = SimpleUnparsedAtomHandler([self.stream_printer_event_handler])
        atom_filter.add_handler(simple_unparsed_atom_handler, stop_when_handled_flag=True)
        atom_filter.add_handler(nmpd)

        # line < max_line_length and log atom matches
        bsla = ByteStreamLineAtomizer(fdme, [], [self.stream_printer_event_handler], 65536, [])
        line = data + b"\n"
        self.assertEqual(bsla.consume_data(line, False), len(line))
        self.assertIsNone(bsla.last_unconsumed_log_atom)
        self.assertEqual(self.output_stream.getvalue(), "")
        bsla = ByteStreamLineAtomizer(fdme, [atom_filter], [self.stream_printer_event_handler], 65536, [])
        self.assertEqual(bsla.consume_data(line, False), len(line))
        self.assertEqual(self.output_stream.getvalue(), output)
        self.reset_output_stream()
        self.assertIsNone(bsla.last_unconsumed_log_atom)

        # line < max_line_length and no match
        no_match = b" no match\n"
        self.assertEqual(bsla.consume_data(no_match, False), len(no_match))
        self.assertEqual(self.output_stream.getvalue(), unparsed)
        self.reset_output_stream()
        self.assertIsNone(bsla.last_unconsumed_log_atom)

        # line > max_line_length and log atom matches
        bsla = ByteStreamLineAtomizer(fdme, [atom_filter], [self.stream_printer_event_handler], 5, [])
        self.assertEqual(bsla.consume_data(line, False), len(line))
        self.assertEqual(self.output_stream.getvalue(), overlong)
        self.assertIsNone(bsla.last_unconsumed_log_atom)
        self.reset_output_stream()
        bsla = ByteStreamLineAtomizer(fdme, [atom_filter], [self.stream_printer_event_handler], 5, [])
        self.assertEqual(bsla.consume_data(data, False), len(data))
        self.assertEqual(self.output_stream.getvalue(), start_overlong)
        self.assertIsNone(bsla.last_unconsumed_log_atom)
        self.reset_output_stream()
        bsla = ByteStreamLineAtomizer(fdme, [atom_filter], [self.stream_printer_event_handler], 5, [])
        self.assertEqual(bsla.consume_data(data, True), len(data))
        self.assertEqual(self.output_stream.getvalue(), start_overlong + overlong_end)
        self.assertIsNone(bsla.last_unconsumed_log_atom)
        self.reset_output_stream()
        bsla = ByteStreamLineAtomizer(fdme, [atom_filter], [self.stream_printer_event_handler], 65536, [])
        self.assertEqual(bsla.consume_data(data, True), len(data))
        self.assertEqual(self.output_stream.getvalue(), incomplete)
        self.assertIsNone(bsla.last_unconsumed_log_atom)
        self.reset_output_stream()

        # use_real_time
        bsla = ByteStreamLineAtomizer(fdme, [atom_filter], [self.stream_printer_event_handler], 65536, [], use_real_time=True)
        self.assertEqual(bsla.consume_data(line, False), len(line))
        self.assertEqual(self.output_stream.getvalue().split(" ", 2)[-1], output)  # skip datetime
        self.reset_output_stream()
        self.assertIsNone(bsla.last_unconsumed_log_atom)

    def test2consume_data_json(self):
        """
        Test the functionality of the ByteStreamLineAtomizer on json data.
        Correct parsing of json data using a state machine is tested in the JsonStateMachineTest.
        """
        # line < max_line_length
        data = b"fixed data"
        fdme = DummyFixedDataModelElement("fixed", data)
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=False, output_logline=False)
        atom_filter = AtomFilters.SubhandlerFilter(None)
        simple_unparsed_atom_handler = SimpleUnparsedAtomHandler([self.stream_printer_event_handler])
        atom_filter.add_handler(simple_unparsed_atom_handler, stop_when_handled_flag=True)
        atom_filter.add_handler(nmpd)
        json_data = b'{\n\t"a": 1,\n\t"b": {"x": 2}}'
        data = b"some log line."
        bsla = ByteStreamLineAtomizer(fdme, [atom_filter], [self.stream_printer_event_handler], 65536, [], json_format=True)
        self.assertEqual(bsla.consume_data(json_data + data, False), len(json_data))

        # this is no valid json and should process only data until the last \n
        self.assertEqual(bsla.consume_data(data + json_data + data, False), len(data) + json_data.rfind(b"\n") + 1)

        json_data = b'{"a": 1, "b": {"c": 2}, "d": 3}\n{"a": 1, "b": {"c": 2}, "d": 3}'
        self.assertEqual(bsla.consume_data(json_data, False), len(json_data))
        self.assertEqual(bsla.consume_data(json_data + data, False), len(json_data))

        json_data = b'{\n\t"a": 1,\n\t"b": {\n\t\t"c": 2},\n\t"d": 3}{\n"a": 1,\n\t"b": {\n\t\t"c": 2},\n\t"d": 3}'
        self.assertEqual(bsla.consume_data(json_data + data, False), len(json_data))
        self.assertEqual(bsla.consume_data(data + json_data, False), len(data) + json_data.rfind(b"\n") + 1)

        # even when the first json data gets invalidated, the second one starts after an empty line and is therefore valid until the end.
        json_data = b'{\n\t"a": 1,\n\t"b": {\n\t\t"c": 2},\n\t"d": 3}\n\n{\n"a": 1,\n\t"b": {\n\t\t"c": 2},\n\t"d": 3}'
        self.assertEqual(bsla.consume_data(json_data + data, False), len(json_data))
        self.assertEqual(bsla.consume_data(data + json_data + data, False), len(data) + len(json_data))

        # this is an incomplete json, but it still can be valid.
        json_data = b'{"a": 1, "b": {"c": 2}, "d": 3}\n{"a": 1, "b": {"c": 2}, "d'
        self.assertEqual(bsla.consume_data(json_data, False), json_data.rfind(b"\n") + 1)

        # this is an incomplete json and the end can not be valid.
        json_data = b'{"a": 1, "b": {"c": 2}, "d": 3}\n{"a": 1, "b": {"c": 2}, d'
        self.assertEqual(bsla.consume_data(json_data, False), json_data.rfind(b"\n") + 1)
        self.reset_output_stream()

        # line > max_line_length
        json_data = b'{\n\t"a": 1,\n\t"b": {\n\t\t"c": 2},\n\t"d": 3}\n{\n"a": 1,\n\t"b": {"c": 2},"d": 3}\n'
        json2 = b'{"a": 1,"b": {"c": 2},"d": 3}{"a": 1,"b": {"c": 2},"d": 3'
        bsla = ByteStreamLineAtomizer(fdme, [], [self.stream_printer_event_handler], 25, [], json_format=True)
        self.assertEqual(bsla.consume_data(json_data, False), json_data.rfind(b'\n') + 1)
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(bsla.consume_data(json_data, True), len(json_data))
        self.assertEqual(self.output_stream.getvalue(), "")
        bsla = ByteStreamLineAtomizer(fdme, [], [self.stream_printer_event_handler], 100, [], json_format=True)
        self.assertEqual(bsla.consume_data(json_data, False), len(json_data))
        self.assertEqual(self.output_stream.getvalue(), "")
        self.assertEqual(bsla.consume_data(json_data, True), len(json_data))
        self.assertEqual(self.output_stream.getvalue(), "")

        bsla = ByteStreamLineAtomizer(fdme, [], [self.stream_printer_event_handler], 25, [], json_format=True)
        self.assertEqual(bsla.consume_data(json2, True), len(json2))
        self.assertEqual(self.output_stream.getvalue(), 'Overlong line terminated by end of stream (1 lines)\n  {"a": 1,"b": {"c": 2},"d":'
                                                        ' 3}{"a": 1,"b": {"c": 2},"d": 3\n\n')
        self.reset_output_stream()
        self.assertEqual(bsla.consume_data(json2, False), len(json2))
        self.assertEqual(self.output_stream.getvalue(), "")
        bsla = ByteStreamLineAtomizer(fdme, [], [self.stream_printer_event_handler], 100, [], json_format=True)
        self.assertEqual(bsla.consume_data(json2, True), len(json2))
        self.assertEqual(self.output_stream.getvalue(), 'Incomplete last line (1 lines)\n  {"a": 1,"b": {"c": 2},"d": 3\n\n')
        self.reset_output_stream()
        self.assertEqual(bsla.consume_data(json2, False), len(json2.rsplit(b"}", 2)[0]) + 1)
        self.assertEqual(self.output_stream.getvalue(), "")

    def test3consume_data_xml(self):
        """
        Test the functionality of the ByteStreamLineAtomizer on xml data.
        The ByteStreamLineAtomizer is not expected to do anything other than passing the data to the XmlModelElement.
        """
        data = b"<messages><note id=\"501\"><to>Tove</to><from>Jani</from><heading/><body><text1>Don't forget me this weekend!</text1><text2>Don't forget me this weekend!</text2></body>" \
               b"</note><note id=\"502\" opt=\"text\"><to>Jani</to><from>Tove</from><heading>Re: </heading><body><text1>I will not</text1><text2>I will not</text2></body></note></messages>"
        output = ("New path(s) detected\nNewMatchPathDetector: \"None\" (1 lines)\n  ['/xml', '/xml/messages/note/+id/id', '/xml/messages/note/to/to', '/xml/messages/note/from/from', "
                  "'/xml/messages/note/body/text1/text1', '/xml/messages/note/body/text2/text2', '/xml/messages/note/+id/id/0', '/xml/messages/note/to/to/0', '/xml/messages/note/from/from/0',"
                  " '/xml/messages/note/?heading', '/xml/messages/note/body/text1/text1/0', '/xml/messages/note/body/text2/text2/0', '/xml/messages/note/+id/id/1', '/xml/messages/note/_+opt/opt',"
                  " '/xml/messages/note/to/to/1', '/xml/messages/note/from/from/1', '/xml/messages/note/?heading/heading', '/xml/messages/note/body/text1/text1/1', '/xml/messages/note/body/text2/text2/1']\n\n")
        key_parser_dict = {"messages": [{"note": {
            "+id": DummyNumberModelElement("id"),
            "_+opt": DummyFixedDataModelElement("opt", b"text"),
            "to": AnyByteDataModelElement("to"),
            "from": AnyByteDataModelElement("from"),
            "?heading": AnyByteDataModelElement("heading"),
            "body": {
                "text1": AnyByteDataModelElement("text1"),
                "text2": AnyByteDataModelElement("text2")
            }
        }}]}
        xmlme = XmlModelElement("xml", key_parser_dict)
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], learn_mode=False, output_logline=False)
        atom_filter = AtomFilters.SubhandlerFilter(None)
        simple_unparsed_atom_handler = SimpleUnparsedAtomHandler([self.stream_printer_event_handler])
        atom_filter.add_handler(simple_unparsed_atom_handler, stop_when_handled_flag=True)
        atom_filter.add_handler(nmpd)
        bsla = ByteStreamLineAtomizer(xmlme, [atom_filter], [self.stream_printer_event_handler], 65536, [], xml_format=True)
        self.assertEqual(bsla.consume_data(data, False), len(data))
        self.assertEqual(self.output_stream.getvalue(), output)

    def test4validate_parameters(self):
        """Test all initialization parameters for the atomizer. Input parameters must be validated in the class."""
        data = b"fixed data"
        fdme = DummyFixedDataModelElement("fixed", data)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, "default", [], [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, b"Default", [], [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, None, [], [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, True, [], [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, 123, [], [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, 123.3, [], [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, ["default"], [], [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, {"id": "Default"}, [], [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, (), [], [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, set(), [], [self.stream_printer_event_handler], 100, [])

        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, "default", [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, b"Default", [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, True, [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, 123, [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, 123.3, [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, ["default"], [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, {"id": "Default"}, [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, (), [self.stream_printer_event_handler], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, set(), [self.stream_printer_event_handler], 100, [])

        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], "default", 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], b"Default", 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], None, 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], True, 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], 123, 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], 123.3, 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], ["default"], 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], {"id": "Default"}, 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], (), 100, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], set(), 100, [])

        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], "default", [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], b"Default", [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], None, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], True, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 123.3, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], ["default"], [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], {"id": "Default"}, [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], (), [])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], set(), [])
        self.assertRaises(ValueError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 0, [])
        self.assertRaises(ValueError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], -1, [])

        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, "default")
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, b"Default")
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, None)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, True)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, 123)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, 123.3)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [b"default"])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, {"id": "Default"})
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, ())
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, set())

        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], eol_sep="default")
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], eol_sep=None)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], eol_sep=True)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], eol_sep=123)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], eol_sep=123.3)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], eol_sep=[b"default"])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], eol_sep={"id": "Default"})
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], eol_sep=())
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], eol_sep=set())
        self.assertRaises(ValueError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], eol_sep=b"")

        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], json_format="default")
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], json_format=b"Default")
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], json_format=None)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], json_format=123)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], json_format=123.3)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], json_format=[b"default"])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], json_format={"id": "Default"})
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], json_format=())
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], json_format=set())

        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], xml_format="default")
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], xml_format=b"Default")
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], xml_format=None)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], xml_format=123)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], xml_format=123.3)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], xml_format=[b"default"])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], xml_format={"id": "Default"})
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], xml_format=())
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], xml_format=set())
        self.assertRaises(ValueError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], json_format=True, xml_format=True)

        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], use_real_time="default")
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], use_real_time=b"Default")
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], use_real_time=None)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], use_real_time=123)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], use_real_time=123.3)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], use_real_time=[b"default"])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], use_real_time={"id": "Default"})
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], use_real_time=())
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], use_real_time=set())

        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], resource_name=True)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], resource_name=123)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], resource_name=123.3)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], resource_name=[b"default"])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], resource_name={"id": "Default"})
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], resource_name=())
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], resource_name=set())

        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], continuous_timestamp_missing_warning="default")
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], continuous_timestamp_missing_warning=b"Default")
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], continuous_timestamp_missing_warning=None)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], continuous_timestamp_missing_warning=123)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], continuous_timestamp_missing_warning=123.3)
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], continuous_timestamp_missing_warning=[b"default"])
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], continuous_timestamp_missing_warning={"id": "Default"})
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], continuous_timestamp_missing_warning=())
        self.assertRaises(TypeError, ByteStreamLineAtomizer, fdme, [], [self.stream_printer_event_handler], 100, [], continuous_timestamp_missing_warning=set())
        ByteStreamLineAtomizer(fdme, [], [], 65536, ["path"], resource_name="test1")
        ByteStreamLineAtomizer(fdme, None, [], 65536, [], resource_name=b"test1")


if __name__ == "__main__":
    unittest.main()
