import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.analysis.MatchValueStreamWriter import MatchValueStreamWriter
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummySequenceModelElement
from io import StringIO, BytesIO, TextIOWrapper, BufferedReader, BufferedRandom, FileIO, BufferedWriter, TextIOBase


class MatchValueStreamWriterTest(TestBase):
    """Unittests for the MatchValueStreamWriter."""

    def test1receive_atom(self):
        """Test if log atoms are processed correctly."""
        euro = b"Euro"
        euro_char = b"\x80"
        number = b"25537"
        space = b" "
        description = "Test1MatchValueStreamWriter"
        match_context = MatchContext(b"25537 Euro "*100)
        fdme_number = DummyFixedDataModelElement("s1", number)
        fdme_sp = DummyFixedDataModelElement("sp", space)
        fdme_euro = DummyFixedDataModelElement("s2", euro)
        fdme_euro_char = DummyFixedDataModelElement("s3", euro_char)
        sme = DummySequenceModelElement("sequence", [fdme_number, fdme_sp, fdme_euro, fdme_sp])
        mvsw = MatchValueStreamWriter(self.output_stream, ["match/sequence/s1", "match/sequence/sp", "match/sequence/s2", "match/sequence/sp"], b";", b"-")
        self.analysis_context.register_component(mvsw, description)
        match_element = sme.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, mvsw)

        # This test case sets up a set of values, which are all expected to be matched.
        mvsw.receive_atom(log_atom)
        mvsw.receive_atom(log_atom)

        self.assertEqual(self.output_stream.getvalue(), "25537; ;Euro; \n"*2)
        self.reset_output_stream()

        # The seperator string is empty, so all values are expected to be one string.
        mvsw.separator = b""
        mvsw.missing_value_string = b"-"

        mvsw.receive_atom(log_atom)
        mvsw.receive_atom(log_atom)
        mvsw.receive_atom(log_atom)
        mvsw.receive_atom(log_atom)

        self.assertEqual(self.output_stream.getvalue(), "25537 Euro \n"*4)
        self.reset_output_stream()

        # The missing value string is empty, so when a string does not match it is simply ignored.
        mvsw.separator = b";"
        mvsw.missing_value_string = b""

        mvsw.receive_atom(log_atom)
        mvsw.receive_atom(log_atom)
        mvsw.receive_atom(log_atom)
        mvsw.receive_atom(log_atom)

        self.assertEqual(self.output_stream.getvalue(), "25537; ;Euro; \n"*4)
        self.reset_output_stream()

        # a set of values which are all expected to be matched with missing values.
        mvsw.separator = b";"
        mvsw.missing_value_string = b"-"

        mvsw.receive_atom(log_atom)
        mvsw.receive_atom(log_atom)
        mvsw.receive_atom(log_atom)
        other_sme = DummySequenceModelElement("sequence", [fdme_number, fdme_sp])
        match_element = other_sme.get_match_element("match", match_context)
        other_log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, mvsw)
        mvsw.receive_atom(other_log_atom)

        self.assertEqual(self.output_stream.getvalue(), "25537; ;Euro; \n"*3 + "25537; ;-;-\n")
        self.reset_output_stream()

        # multiple spaces, but "Euro" string is missing.
        mvsw = MatchValueStreamWriter(self.output_stream, ["match/sequence/s1", "match/sequence/sp", "match/sequence/s2", "match/sequence/sp", "match/sequence/sp"], b";", b"-")
        match_context = MatchContext(b"25537  ")
        mvsw.receive_atom(log_atom)
        mvsw.receive_atom(log_atom)
        mvsw.receive_atom(log_atom)
        other_sme = DummySequenceModelElement("sequence", [fdme_number, fdme_sp, fdme_sp])
        match_element = other_sme.get_match_element("match", match_context)
        other_log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, mvsw)
        mvsw.receive_atom(other_log_atom)

        self.assertEqual(self.output_stream.getvalue(), "25537; ;Euro; ;-\n"*3 + "25537; ;-; ;-\n")
        self.reset_output_stream()

        # multiple spaces, but "Euro" string is missing and only one space path being searched.
        mvsw = MatchValueStreamWriter(self.output_stream, ["match/sequence/s1", "match/sequence/s3", "match/sequence/sp"], b";", b"-")
        match_context = MatchContext(b"25537\x80 ")
        other_sme = DummySequenceModelElement("sequence", [fdme_number, fdme_euro_char, fdme_sp])
        match_element = other_sme.get_match_element("match", match_context)
        other_log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, mvsw)
        mvsw.receive_atom(other_log_atom)

        self.assertEqual(self.output_stream.getvalue(), "25537;; \n")
        self.reset_output_stream()

        # test with non-ascii characters

    def test2validate_parameters(self):
        """Test all initialization parameters for the detector. Input parameters must be validated in the class."""
        self.assertRaises(TypeError, MatchValueStreamWriter, None, ["path"], b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, 123, ["path"], b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, 123.3, ["path"], b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, "", ["path"], b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, b"", ["path"], b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, True, ["path"], b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, {"id": "Default"}, ["path"], b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, ["Default"], ["path"], b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, (), ["path"], b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, set(), ["path"], b";", b"-")

        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), None, b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), 123, b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), 123.3, b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), "path", b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), b"path", b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), True, b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), {"id": "Default"}, b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), (), b";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), set(), b";", b"-")

        self.assertRaises(ValueError, MatchValueStreamWriter, StringIO(), ["path"], b"", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], ";", b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], None, b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], 123, b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], 123.2, b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], True, b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], {"id": "Default"}, b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], (), b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], [b";"], b"-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], set(b";"), b"-")


        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], b";", "-")
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], b";", None)
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], b";", 123)
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], b";", 123.3)
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], b";", True)
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], b";", {"id": "Default"})
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], b";", ())
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], b";", [b"-"])
        self.assertRaises(TypeError, MatchValueStreamWriter, StringIO(), ["path"], b";", set(b";"))

        MatchValueStreamWriter(StringIO(), ["path"], b";", b"")
        MatchValueStreamWriter(StringIO(), ["path"], b";", b"-")
        MatchValueStreamWriter(BytesIO(), ["path"], b";", b"-")
        with FileIO("/dev/null") as f:
            MatchValueStreamWriter(f, ["path"], b";", b"-")
        MatchValueStreamWriter(BufferedWriter(StringIO()), ["path"], b";", b"-")


if __name__ == "__main__":
    unittest.main()
