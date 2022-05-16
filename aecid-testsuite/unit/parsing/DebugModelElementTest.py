import unittest
import sys
from _io import StringIO
from aminer.parsing.DebugModelElement import DebugModelElement
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase, DummyMatchContext


class DebugModelElementTest(TestBase):
    """Unittests for the DebugModelElement."""

    id_ = "debug"
    path = "path"

    def test1get_id(self):
        """Test if get_id works properly."""
        old_stderr = sys.stderr
        output = StringIO()
        sys.stderr = output
        debug_me = DebugModelElement(self.id_)
        self.assertEqual(debug_me.get_id(), self.id_)
        self.assertEqual("DebugModelElement %s added\n" % self.id_, output.getvalue())
        sys.stderr = old_stderr

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        old_stderr = sys.stderr
        output = StringIO()
        sys.stderr = output
        debug_me = DebugModelElement(self.id_)
        self.assertEqual(debug_me.get_child_elements(), None)
        self.assertEqual("DebugModelElement %s added\n" % self.id_, output.getvalue())
        sys.stderr = old_stderr

    def test3get_match_element_valid_match(self):
        """Parse data and check if the MatchContext was not changed."""
        old_stderr = sys.stderr
        output = StringIO()
        sys.stderr = output
        debug_model_element = DebugModelElement(self.id_)
        self.assertEqual(output.getvalue(), "DebugModelElement %s added\n" % self.id_)

        output.seek(0)
        output.truncate(0)

        data = b"some data"
        match_context = DummyMatchContext(data)
        match_element = debug_model_element.get_match_element(self.path, match_context)
        self.assertEqual(
            output.getvalue(), 'DebugModelElement path = "%s", unmatched = "%s"\n' % (match_element.get_path(), repr(
                match_context.match_data)))
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, b"", b"", None)

        output.seek(0)
        output.truncate(0)

        data = b"123 0x2a. [\"abc\"]:"
        match_context = DummyMatchContext(data)
        match_element = debug_model_element.get_match_element(self.path, match_context)
        self.assertEqual(
            output.getvalue(), 'DebugModelElement path = "%s", unmatched = "%s"\n' % (match_element.get_path(), repr(
                match_context.match_data)))
        self.compare_match_results(data, match_element, match_context, self.id_, self.path, b"", b"", None)

        sys.stderr = old_stderr

    def test4element_id_input_validation(self):
        """Check if element_id is validated."""
        self.assertRaises(ValueError, DebugModelElement, "")  # empty element_id
        self.assertRaises(TypeError, DebugModelElement, None)  # None element_id
        self.assertRaises(TypeError, DebugModelElement, b"path")  # bytes element_id is not allowed
        self.assertRaises(TypeError, DebugModelElement, True)  # bool element_id is not allowed
        self.assertRaises(TypeError, DebugModelElement, 123)  # integer element_id is not allowed
        self.assertRaises(TypeError, DebugModelElement, 123.22)  # float element_id is not allowed
        self.assertRaises(TypeError, DebugModelElement, {"id": "path"})  # dict element_id is not allowed
        self.assertRaises(TypeError, DebugModelElement, ["path"])  # list element_id is not allowed
        self.assertRaises(TypeError, DebugModelElement, [])  # empty list element_id is not allowed
        self.assertRaises(TypeError, DebugModelElement, ())  # empty tuple element_id is not allowed
        self.assertRaises(TypeError, DebugModelElement, set())  # empty set element_id is not allowed

    def test5get_match_element_match_context_input_validation(self):
        """Check if an exception is raised, when other classes than MatchContext are used in get_match_element."""
        model_element = DebugModelElement(self.id_)
        data = b"abcdefghijklmnopqrstuvwxyz.!?"
        model_element.get_match_element(self.path, DummyMatchContext(data))
        model_element.get_match_element(self.path, MatchContext(data))

        self.assertRaises(AttributeError, model_element.get_match_element, self.path, MatchElement(self.path, data, None, None))
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, data.decode())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, True)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, 123.22)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, None)
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, [])
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, {"key": MatchContext(data)})
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, set())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, ())
        self.assertRaises(AttributeError, model_element.get_match_element, self.path, model_element)


if __name__ == "__main__":
    unittest.main()
