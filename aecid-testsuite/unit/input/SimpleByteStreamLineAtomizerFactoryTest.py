import unittest
from aminer.input.SimpleByteStreamLineAtomizerFactory import SimpleByteStreamLineAtomizerFactory
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from unit.TestBase import TestBase, DummyFixedDataModelElement


class SimpleByteStreamLineAtomizerFactoryTest(TestBase):
    """The SimpleByteStreamLineAtomizerFactory should return a valid ByteStreamLineAtomizer with all parameters of the Factory."""

    def test1get_atomizer(self):
        """Tests the creating of an SimpleByteStreamLineAtomizer with the Factory."""
        fdme = DummyFixedDataModelElement("fixed", b"fixed data")
        nmpd1 = NewMatchPathDetector(self.aminer_config, [], "Default", False)
        nmpd2 = NewMatchPathDetector(self.aminer_config, [], "Default", False)

        sbslaf = SimpleByteStreamLineAtomizerFactory(fdme, [nmpd1, nmpd2], [self.stream_printer_event_handler], None)

        bsla = sbslaf.get_atomizer_for_resource(None)
        self.assertEqual(bsla.atom_handler_list, [nmpd1, nmpd2])
        self.assertEqual(bsla.event_handler_list, [self.stream_printer_event_handler])
        self.assertEqual(bsla.default_timestamp_path_list, [])
        self.assertEqual(bsla.parsing_model, fdme)
        self.assertEqual(bsla.max_line_length, 65536)
        self.assertEqual(bsla.resource_name, None)

    def test2validate_parameters(self):
        """Test all initialization parameters for the atomizer. Input parameters must be validated in the class."""
        data = b"fixed data"
        fdme = DummyFixedDataModelElement("fixed", data)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, "default", [], [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, b"Default", [], [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, None, [], [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, True, [], [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, 123, [], [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, 123.3, [], [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, ["default"], [], [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, {"id": "Default"}, [], [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, (), [], [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, set(), [], [self.stream_printer_event_handler], [])

        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, "default", [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, b"Default", [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, True, [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, 123, [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, 123.3, [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, ["default"], [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, {"id": "Default"}, [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, (), [self.stream_printer_event_handler], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, set(), [self.stream_printer_event_handler], [])

        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], "default", [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], b"Default", [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], None, [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], True, [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], 123, [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], 123.3, [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], ["default"], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], {"id": "Default"}, [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], (), [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], set(), [])

        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], "default", [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], b"Default", [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], None, [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], True, [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], 123.3, [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], ["default"], [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], {"id": "Default"}, [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], (), [])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], set(), [])

        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], "default")
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], b"Default")
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], True)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], 123)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], 123.3)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [b"default"])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], {"id": "Default"})
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], ())
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], set())
        SimpleByteStreamLineAtomizerFactory(fdme, [], [self.stream_printer_event_handler], None)

        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], eol_sep="default")
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], eol_sep=None)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], eol_sep=True)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], eol_sep=123)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], eol_sep=123.3)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], eol_sep=[b"default"])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], eol_sep={"id": "Default"})
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], eol_sep=())
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], eol_sep=set())
        self.assertRaises(ValueError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], eol_sep=b"")

        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], json_format="default")
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], json_format=b"Default")
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], json_format=None)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], json_format=123)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], json_format=123.3)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], json_format=[b"default"])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], json_format={"id": "Default"})
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], json_format=())
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], json_format=set())

        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], xml_format="default")
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], xml_format=b"Default")
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], xml_format=None)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], xml_format=123)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], xml_format=123.3)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], xml_format=[b"default"])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], xml_format={"id": "Default"})
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], xml_format=())
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], xml_format=set())
        self.assertRaises(ValueError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], json_format=True, xml_format=True)

        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], use_real_time="default")
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], use_real_time=b"Default")
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], use_real_time=None)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], use_real_time=123)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], use_real_time=123.3)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], use_real_time=[b"default"])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], use_real_time={"id": "Default"})
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], use_real_time=())
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], use_real_time=set())

        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], continuous_timestamp_missing_warning="default")
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], continuous_timestamp_missing_warning=b"Default")
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], continuous_timestamp_missing_warning=None)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], continuous_timestamp_missing_warning=123)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], continuous_timestamp_missing_warning=123.3)
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], continuous_timestamp_missing_warning=[b"default"])
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], continuous_timestamp_missing_warning={"id": "Default"})
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], continuous_timestamp_missing_warning=())
        self.assertRaises(TypeError, SimpleByteStreamLineAtomizerFactory, fdme, [], [self.stream_printer_event_handler], [], continuous_timestamp_missing_warning=set())
        SimpleByteStreamLineAtomizerFactory(fdme, [], [], ["path"])
        SimpleByteStreamLineAtomizerFactory(fdme, None, [], [])


if __name__ == "__main__":
    unittest.main()
