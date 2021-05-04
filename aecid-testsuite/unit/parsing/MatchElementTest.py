import unittest
from aminer.parsing.MatchElement import MatchElement
from unit.TestBase import TestBase


class MatchElementTest(TestBase):
    """Unittests for the MatchElement."""

    path = "path"
    match_string = b"12.5"
    match_object = 12.5

    def test1get_path(self):
        """Test if get_path works properly."""
        match_element = MatchElement(self.path, self.match_string, self.match_object, None)
        self.assertEqual(match_element.get_path(), self.path)

    def test2get_match_string(self):
        """Test if get_match_string returns None."""
        match_element = MatchElement(self.path, self.match_string, self.match_object, None)
        self.assertEqual(match_element.get_match_string(), self.match_string)

    def test3get_match_object(self):
        """Test if get_match_string returns None."""
        match_element = MatchElement(self.path, self.match_string, self.match_object, None)
        self.assertEqual(match_element.get_match_object(), self.match_object)

    def test4get_children(self):
        """Test if get_match_string returns None."""
        match_element = MatchElement(self.path, self.match_string, self.match_object, None)
        self.assertEqual(match_element.get_children(), None)

    def test5annotate_match(self):
        """This test case checks if all possible annotations are created correctly."""
        a3 = MatchElement("a3", b"a3", b"a3", None)
        a2 = MatchElement("a2", b"a2", b"a2", [a3])
        a1 = MatchElement("a1", b"a1", b"a1", [a2])
        b3 = MatchElement("b3", b"b3", b"b3", None)
        b2 = MatchElement("b2", b"b2", b"b2", [b3])
        b1 = MatchElement("b1", b"b1", b"b1", [b2])
        root_element = MatchElement("root", b"root", b"root", [a1, b1])

        self.assertEqual(root_element.annotate_match(None), "root: root a1: a1 a2: a2 a3: a3 b1: b1 b2: b2 b3: b3")
        self.assertEqual(root_element.annotate_match(""), "root: root\n  a1: a1\n    a2: a2\n      a3: a3\n  b1: b1\n    b2: b2\n      "
                                                          "b3: b3")
        self.assertEqual(root_element.annotate_match("--"), "--root: root\n--  a1: a1\n--    a2: a2\n--      a3: a3\n--  b1: b1\n"
                                                            "--    b2: b2\n--      b3: b3")

    def test6serialize_object(self):
        """This test case checks if all child objects are serialized correctly."""
        a3 = MatchElement("a3", b"a3", b"a3", None)
        a2 = MatchElement("a2", b"a2", b"a2", [a3])
        a1 = MatchElement("a1", b"a1", b"a1", [a2])
        b3 = MatchElement("b3", b"b3", b"b3", None)
        b2 = MatchElement("b2", b"b2", b"b2", [b3])
        b1 = MatchElement("b1", b"b1", b"b1", [b2])
        root_element = MatchElement("root", b"root", b"root", [a1, b1])

        self.assertEqual(root_element.serialize_object(), {"path": "root", "match_object": b"root", "match_string": b"root", "children": [
            {"path": "a1", "match_object": b"a1", "match_string": b"a1", "children": [
                {"path": "a2", "match_object": b"a2", "match_string": b"a2",
                    "children": [{"path": "a3", "match_object": b"a3", "match_string": b"a3", "children": []}]}]},
            {"path": "b1", "match_object": b"b1", "match_string": b"b1", "children": [
                {"path": "b2", "match_object": b"b2", "match_string": b"b2",
                    "children": [{"path": "b3", "match_object": b"b3", "match_string": b"b3", "children": []}]}]}]})

    def test7str(self):
        """Test the string representation of the MatchElements."""
        a3 = MatchElement("a3", b"a3", b"a3", None)
        a2 = MatchElement("a2", b"a2", b"a2", [a3])
        a1 = MatchElement("a1", b"a1", b"a1", [a2])
        b3 = MatchElement("b3", b"b3", b"b3", None)
        b2 = MatchElement("b2", b"b2", b"b2", [b3])
        b1 = MatchElement("b1", b"b1", b"b1", [b2])
        root_element = MatchElement("root", b"root", b"root", [a1, b1])
        self.assertEqual(root_element.__str__(), "MatchElement: path = root, string = root, object = root, children = 2")

        root_element = MatchElement("match", b"string", 2, None)
        self.assertEqual(root_element.__str__(), "MatchElement: path = match, string = string, object = 2, children = 0")

    def test8init_path_input_validation(self):
        """Check if path is validated in __init__()."""
        self.assertRaises(TypeError, MatchElement, b"path", self.match_string, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, True, self.match_string, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, 123, self.match_string, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, 123.22, self.match_string, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, {"id": "path"}, self.match_string, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, ["path"], self.match_string, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, [], self.match_string, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, (), self.match_string, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, set(), self.match_string, self.match_object, None)

    def test9init_match_string_input_validation(self):
        """Check if match_string is validated in __init__()."""
        self.assertRaises(TypeError, MatchElement, self.path, "path", self.match_object, None)
        self.assertRaises(TypeError, MatchElement, self.path, True, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, self.path, 123, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, self.path, 123.22, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, self.path, {"id": "path"}, self.match_object, None)
        self.assertRaises(TypeError, MatchElement, self.path, ["path"], self.match_object, None)
        self.assertRaises(TypeError, MatchElement, self.path, [], self.match_object, None)
        self.assertRaises(TypeError, MatchElement, self.path, (), self.match_object, None)
        self.assertRaises(TypeError, MatchElement, self.path, set(), self.match_object, None)

    def test10init_match_object_input_validation(self):
        """Check if match_object is validated in __init__()."""
        MatchElement(self.path, self.match_string, b"", None)
        MatchElement(self.path, self.match_string, "path", None)
        MatchElement(self.path, self.match_string, True, None)
        MatchElement(self.path, self.match_string, 123, None)
        MatchElement(self.path, self.match_string, 123.22, None)
        MatchElement(self.path, self.match_string, {"id": "path"}, None)
        MatchElement(self.path, self.match_string, ["path"], None)
        MatchElement(self.path, self.match_string, [], None)
        MatchElement(self.path, self.match_string, (), None)
        MatchElement(self.path, self.match_string, set(), None)
        MatchElement(self.path, self.match_string, MatchElement(self.path, self.match_string, self.match_object, None), None)

    def test11init_children_input_validation(self):
        """Check if children is validated in __init__()."""
        self.assertRaises(TypeError, MatchElement, self.path, self.match_string, self.match_object, b"path")
        self.assertRaises(TypeError, MatchElement, self.path, self.match_string, self.match_object, "path")
        self.assertRaises(TypeError, MatchElement, self.path, self.match_string, self.match_object, True)
        self.assertRaises(TypeError, MatchElement, self.path, self.match_string, self.match_object, 123)
        self.assertRaises(TypeError, MatchElement, self.path, self.match_string, self.match_object, 123.22)
        self.assertRaises(TypeError, MatchElement, self.path, self.match_string, self.match_object, {"id": "path"})
        self.assertRaises(ValueError, MatchElement, self.path, self.match_string, self.match_object, [])
        self.assertRaises(TypeError, MatchElement, self.path, self.match_string, self.match_object, ())
        self.assertRaises(TypeError, MatchElement, self.path, self.match_string, self.match_object, set())
        self.assertRaises(TypeError, MatchElement, self.path, self.match_string, self.match_object, ["string"])
        self.assertRaises(TypeError, MatchElement, self.path, self.match_string, self.match_object, [b"string"])

    def test12init_child_elements_with_no_path(self):
        """This test case checks, whether an exception is raised, when the path is None and children are passed."""
        self.assertRaises(ValueError, MatchElement, None, self.match_string, self.match_object, [
            MatchElement(self.path, self.match_string, self.match_object, None)])

    def test13annotate_match_indent_str_input_validation(self):
        """Check if indent_str is validated in annotate_match()."""
        match_element = MatchElement(self.path, self.match_string, self.match_object, None)
        self.assertRaises(TypeError, match_element.annotate_match, b"  ")
        self.assertRaises(TypeError, match_element.annotate_match, [" ", "-"])
        self.assertRaises(TypeError, match_element.annotate_match, 123.22)
        self.assertRaises(TypeError, match_element.annotate_match, {"id": "path"})
        self.assertRaises(TypeError, match_element.annotate_match, ["path"])
        self.assertRaises(TypeError, match_element.annotate_match, [])
        self.assertRaises(TypeError, match_element.annotate_match, ())
        self.assertRaises(TypeError, match_element.annotate_match, set())


if __name__ == "__main__":
    unittest.main()
