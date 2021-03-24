import unittest
import sys
from _io import StringIO
from aminer.parsing.DebugModelElement import DebugModelElement
from unit.TestBase import TestBase, DummyMatchContext


class DebugModelElementTest(TestBase):
    """Unittests for the DebugModelElement."""

    #TODO: change checks to be done in TestBase.compare_result()

    def test1get_id(self):
        """Test if get_id works properly."""
        old_stderr = sys.stderr
        output = StringIO()
        sys.stderr = output
        debug_me = DebugModelElement("s0")
        self.assertEqual(debug_me.get_id(), "s0")
        self.assertEqual("DebugModelElement s0 added\n", output.getvalue())
        sys.stderr = old_stderr

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        old_stderr = sys.stderr
        output = StringIO()
        sys.stderr = output
        debug_me = DebugModelElement("s0")
        self.assertEqual(debug_me.get_child_elements(), None)
        self.assertEqual("DebugModelElement s0 added\n", output.getvalue())
        sys.stderr = old_stderr

    def test3get_match_element_valid_match(self):
        """Parse data and check if the MatchContext was not changed."""
        old_stderr = sys.stderr
        output = StringIO()
        sys.stderr = output
        debug_model_element = DebugModelElement('debug')
        self.assertEqual(output.getvalue(), 'DebugModelElement %s added\n' % debug_model_element.element_id)

        output.seek(0)
        output.truncate(0)

        data = b"some data"
        match_context = DummyMatchContext(data)
        match_element = debug_model_element.get_match_element('debugMatch', match_context)
        self.assertEqual(
            output.getvalue(), 'DebugModelElement path = "%s", unmatched = "%s"\n' % (match_element.get_path(), match_context.match_data))
        self.assertEqual(data, match_context.match_data)
        self.assertEqual(b"", match_context.match_string)
        self.assertEqual(match_element.path, "debugMatch/debug")
        self.assertEqual(match_element.match_string, b"")
        self.assertEqual(match_element.match_object, b"")
        self.assertEqual(match_element.children, None)

        output.seek(0)
        output.truncate(0)

        data = b"123 0x2a. [\"abc\"]:"
        match_context = DummyMatchContext(data)
        match_element = debug_model_element.get_match_element('debugMatch', match_context)
        self.assertEqual(
            output.getvalue(), 'DebugModelElement path = "%s", unmatched = "%s"\n' % (match_element.get_path(), match_context.match_data))
        self.assertEqual(data, match_context.match_data)
        self.assertEqual(b"", match_context.match_string)
        self.assertEqual(match_element.path, "debugMatch/debug")
        self.assertEqual(match_element.match_string, b"")
        self.assertEqual(match_element.match_object, b"")
        self.assertEqual(match_element.children, None)

        sys.stderr = old_stderr

    def test4element_id_input_validation(self):
        """Check if element_id is validated."""
        # empty element_id
        element_id = ""
        self.assertRaises(ValueError, DebugModelElement, element_id)

        # None element_id
        element_id = None
        self.assertRaises(TypeError, DebugModelElement, element_id)

        # bytes element_id is not allowed
        element_id = b"path"
        self.assertRaises(TypeError, DebugModelElement, element_id)

        # integer element_id is not allowed
        element_id = 123
        self.assertRaises(TypeError, DebugModelElement, element_id)

        # float element_id is not allowed
        element_id = 123.22
        self.assertRaises(TypeError, DebugModelElement, element_id)

        # dict element_id is not allowed
        element_id = {"id": "path"}
        self.assertRaises(TypeError, DebugModelElement, element_id)

        # list element_id is not allowed
        element_id = ["path"]
        self.assertRaises(TypeError, DebugModelElement, element_id)

        # empty list element_id is not allowed
        element_id = []
        self.assertRaises(TypeError, DebugModelElement, element_id)


if __name__ == "__main__":
    unittest.main()
