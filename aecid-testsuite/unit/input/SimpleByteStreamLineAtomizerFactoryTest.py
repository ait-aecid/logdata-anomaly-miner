import unittest
from aminer.input.SimpleByteStreamLineAtomizerFactory import SimpleByteStreamLineAtomizerFactory
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from unit.TestBase import TestBase


class SimpleByteStreamLineAtomizerFactoryTest(TestBase):
    """The SimpleByteStreamLineAtomizerFactory should return a valid ByteStreamLineAtomizer with all parameters of the Factory."""

    def test1get_atomizer(self):
        any_byte_data_model_element = AnyByteDataModelElement('a1')
        new_match_path_detector1 = NewMatchPathDetector(self.aminer_config, [], 'Default', False)
        new_match_path_detector2 = NewMatchPathDetector(self.aminer_config, [], 'Default', False)

        simple_byte_stream_line_atomizer_factory = SimpleByteStreamLineAtomizerFactory(any_byte_data_model_element, [
            new_match_path_detector1, new_match_path_detector2], [self.stream_printer_event_handler], None)

        byte_stream_line_atomizer = simple_byte_stream_line_atomizer_factory.get_atomizer_for_resource(None)
        self.assertEqual(byte_stream_line_atomizer.atom_handler_list, [new_match_path_detector1, new_match_path_detector2])
        self.assertEqual(byte_stream_line_atomizer.event_handler_list, [self.stream_printer_event_handler])
        self.assertEqual(byte_stream_line_atomizer.default_timestamp_paths, [])
        self.assertEqual(byte_stream_line_atomizer.parsing_model, any_byte_data_model_element)
        self.assertEqual(byte_stream_line_atomizer.max_line_length, 65536)


if __name__ == "__main__":
    unittest.main()
