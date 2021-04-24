import unittest
from aminer.parsing.MatchContext import MatchContext, DebugMatchContext
from unit.TestBase import TestBase


class MatchContextTest(TestBase):
    """Unittests for the MatchContext and DebugMatchContext."""

    def test1update_successful(self):
        """Update the MatchContext and DebugMatchContext with allowed values."""

    def test2update_fail(self):
        """Update the MatchContext and DebugMatchContext with not allowed values."""

    def test3_match_context_init_input_validation(self):
        """Check if input is validated for MatchContext.__init__()."""
        # empty match_data
        match_data = b""
        self.assertRaises(ValueError, MatchContext, match_data)

        # None match_data
        match_data = None
        self.assertRaises(TypeError, MatchContext, match_data)

        # string match_data is not allowed
        match_data = "path"
        self.assertRaises(TypeError, MatchContext, match_data)

        # boolean match_data is not allowed
        match_data = True
        self.assertRaises(TypeError, MatchContext, match_data)

        # integer match_data is not allowed
        match_data = 123
        self.assertRaises(TypeError, MatchContext, match_data)

        # float match_data is not allowed
        match_data = 123.22
        self.assertRaises(TypeError, MatchContext, match_data)

        # dict match_data is not allowed
        match_data = {"id": "path"}
        self.assertRaises(TypeError, MatchContext, match_data)

        # list match_data is not allowed
        match_data = ["path"]
        self.assertRaises(TypeError, MatchContext, match_data)

        # empty list match_data is not allowed
        match_data = []
        self.assertRaises(TypeError, MatchContext, match_data)

        # empty tuple match_data is not allowed
        match_data = ()
        self.assertRaises(TypeError, MatchContext, match_data)

        # empty set match_data is not allowed
        match_data = set()
        self.assertRaises(TypeError, MatchContext, match_data)

    def test4_match_context_update_input_validation(self):
        """Check if MatchContext.update() fails if len(match_string) does not work."""
        data = b"this is an example of a log line."
        match_context = MatchContext(data)
        self.assertRaises(TypeError, match_context.update, None)
        self.assertRaises(TypeError, match_context.update, True)
        self.assertRaises(TypeError, match_context.update, 123)
        self.assertRaises(TypeError, match_context.update, 123.22)

    def test5_debug_match_context_init_input_validation(self):
        """Check if input is validated for DebugMatchContext.__init__()."""
        # empty match_data
        match_data = b""
        self.assertRaises(ValueError, DebugMatchContext, match_data)

        # None match_data
        match_data = None
        self.assertRaises(TypeError, DebugMatchContext, match_data)

        # string match_data is not allowed
        match_data = "path"
        self.assertRaises(TypeError, DebugMatchContext, match_data)

        # bytes match_data is not allowed
        match_data = True
        self.assertRaises(TypeError, DebugMatchContext, match_data)

        # integer match_data is not allowed
        match_data = 123
        self.assertRaises(TypeError, DebugMatchContext, match_data)

        # float match_data is not allowed
        match_data = 123.22
        self.assertRaises(TypeError, DebugMatchContext, match_data)

        # boolean match_data is not allowed
        match_data = True
        self.assertRaises(TypeError, DebugMatchContext, match_data)

        # dict match_data is not allowed
        match_data = {"id": "path"}
        self.assertRaises(TypeError, DebugMatchContext, match_data)

        # list match_data is not allowed
        match_data = ["path"]
        self.assertRaises(TypeError, DebugMatchContext, match_data)

        # empty list match_data is not allowed
        match_data = []
        self.assertRaises(TypeError, DebugMatchContext, match_data)

        # empty tuple match_data is not allowed
        match_data = ()
        self.assertRaises(TypeError, DebugMatchContext, match_data)

        # empty set match_data is not allowed
        match_data = set()
        self.assertRaises(TypeError, DebugMatchContext, match_data)

    def test6_debug_match_context_update_input_validation(self):
        """Check if input is validated for DebugMatchContext.update()."""
        data = b"this is an example of a log line."
        match_context = MatchContext(data)
        self.assertRaises(TypeError, match_context.update, None)
        self.assertRaises(TypeError, match_context.update, True)
        self.assertRaises(TypeError, match_context.update, 123)
        self.assertRaises(TypeError, match_context.update, 123.22)

