import unittest
import sys
import subprocess
from time import time, sleep
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext
from datetime import datetime


class LogAtomTest(TestBase):
    """Unittests for the LogAtom."""

    def test1validate_parameters(self):
        """Test all initialization parameters for the event handler. Input parameters must be validated in the class."""
        mc = DummyMatchContext(b" pid=")
        fdme = DummyFixedDataModelElement("s1", b" pid=")
        me = fdme.get_match_element("", mc)
        pm = ParserMatch(me)

        self.assertRaises(TypeError, LogAtom, "", pm, 1, self)
        self.assertRaises(TypeError, LogAtom, ["default"], pm, 1, self)
        self.assertRaises(TypeError, LogAtom, None, pm, 1, self)
        self.assertRaises(TypeError, LogAtom, True, pm, 1, self)
        self.assertRaises(TypeError, LogAtom, 123, pm, 1, self)
        self.assertRaises(TypeError, LogAtom, 123.3, pm, 1, self)
        self.assertRaises(TypeError, LogAtom, {"id": "Default"}, pm, 1, self)
        self.assertRaises(TypeError, LogAtom, (), pm, 1, self)
        self.assertRaises(TypeError, LogAtom, set(), pm, 1, self)
        self.assertRaises(ValueError, LogAtom, b"", pm, 1, self)

        self.assertRaises(TypeError, LogAtom, fdme.data, "", 1, self)
        self.assertRaises(TypeError, LogAtom, fdme.data, ["default"], 1, self)
        self.assertRaises(TypeError, LogAtom, fdme.data, True, 1, self)
        self.assertRaises(TypeError, LogAtom, fdme.data, 123, 1, self)
        self.assertRaises(TypeError, LogAtom, fdme.data, 123.3, 1, self)
        self.assertRaises(TypeError, LogAtom, fdme.data, {"id": "Default"}, 1, self)
        self.assertRaises(TypeError, LogAtom, fdme.data, (), 1, self)
        self.assertRaises(TypeError, LogAtom, fdme.data, set(), 1, self)
        self.assertRaises(TypeError, LogAtom, fdme.data, b"", 1, self)

        self.assertRaises(TypeError, LogAtom, fdme.data, pm, "", self)
        self.assertRaises(TypeError, LogAtom, fdme.data, pm, ["default"], self)
        self.assertRaises(TypeError, LogAtom, fdme.data, pm, True, self)
        self.assertRaises(TypeError, LogAtom, fdme.data, pm, {"id": "Default"}, self)
        self.assertRaises(TypeError, LogAtom, fdme.data, pm, (), self)
        self.assertRaises(TypeError, LogAtom, fdme.data, pm, set(), self)
        self.assertRaises(TypeError, LogAtom, fdme.data, pm, b"", self)
        LogAtom(b"data", None, None, None)


if __name__ == '__main__':
    unittest.main()
