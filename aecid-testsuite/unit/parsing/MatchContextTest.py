import unittest
from aminer.parsing.MatchContext import MatchContext, DebugMatchContext
from unit.TestBase import TestBase


class MatchContextTest(TestBase):
    """Unittests for the MatchContext and DebugMatchContext."""

    def test1update_successful(self):
        """Update the MatchContext and DebugMatchContext with allowed values."""
        data = b"this is an example of a log line."
        match_context = MatchContext(data)
        match_context.update(b"this is an example")
        self.assertEqual(match_context.match_data, b" of a log line.")

        match_context = MatchContext(data)
        match_context.update([b"t", b"h", b"i", b"s"])
        self.assertEqual(match_context.match_data, b" is an example of a log line.")

        match_context = MatchContext(data)
        match_context.update(b"some other text")
        self.assertEqual(match_context.match_data, b"ple of a log line.")

        match_context = DebugMatchContext(data)
        match_context.update(b"this is an example ")
        self.assertEqual(match_context.match_data, b"of a log line.")
        self.assertEqual(match_context.get_debug_info(),
                         'Starting match update on "this is an example of a log line."\n  Removed: "this is an example ", remaining 14'
                         ' bytes\n  Shortest unmatched data: "of a log line."\n')
        self.assertEqual(match_context.get_debug_info(), '  Shortest unmatched data: "of a log line."\n')
        match_context.update(b"of")
        self.assertEqual(match_context.get_debug_info(), '  Removed: "of", remaining 12 bytes\n  Shortest unmatched data: " a log line."\n')
        match_context.update(b" a log line.")
        self.assertEqual(match_context.get_debug_info(), '  Removed: " a log line.", remaining 0 bytes\n  Shortest unmatched data: ""\n')
        self.assertRaises(ValueError, match_context.update, b" a log line.")
        self.assertEqual(
            match_context.get_debug_info(), '  Current data  does not start with " a log line."\n  Shortest unmatched data: ""\n')

    def test2update_fail(self):
        """Update the DebugMatchContext with not allowed values."""
        match_context = DebugMatchContext(b"this is an example of a log line.")
        self.assertRaises(TypeError, match_context.update, "this is an example")
        self.assertRaises(TypeError, match_context.update, [b"t", b"h", b"i", b"s"])
        self.assertRaises(ValueError, match_context.update, b"some other text")
        self.assertRaises(ValueError, match_context.update, b"")

    def test3_match_context_init_input_validation(self):
        """Check if input is validated for MatchContext.__init__()."""
        self.assertRaises(ValueError, MatchContext, b"")
        self.assertRaises(TypeError, MatchContext, None)
        self.assertRaises(TypeError, MatchContext, "path")
        self.assertRaises(TypeError, MatchContext, True)
        self.assertRaises(TypeError, MatchContext, 123)
        self.assertRaises(TypeError, MatchContext, 123.22)
        self.assertRaises(TypeError, MatchContext, {"id": "path"})
        self.assertRaises(TypeError, MatchContext, ["path"])
        self.assertRaises(TypeError, MatchContext, [])
        self.assertRaises(TypeError, MatchContext, ())
        self.assertRaises(TypeError, MatchContext, set())

    def test4_match_context_update_input_validation(self):
        """Check if MatchContext.update() fails if len(match_string) does not work."""
        data = b"this is an example of a log line."
        match_context = MatchContext(data)
        self.assertRaises(TypeError, match_context.update, None)
        self.assertRaises(TypeError, match_context.update, True)
        self.assertRaises(TypeError, match_context.update, 123)
        self.assertRaises(TypeError, match_context.update, 123.22)
        self.assertRaises(TypeError, match_context.update, match_context)

    def test5_debug_match_context_init_input_validation(self):
        """Check if input is validated for DebugMatchContext.__init__()."""
        self.assertRaises(ValueError, DebugMatchContext, b"")
        self.assertRaises(TypeError, DebugMatchContext, None)
        self.assertRaises(TypeError, DebugMatchContext, "path")
        self.assertRaises(TypeError, DebugMatchContext, True)
        self.assertRaises(TypeError, DebugMatchContext, 123)
        self.assertRaises(TypeError, DebugMatchContext, 123.22)
        self.assertRaises(TypeError, DebugMatchContext, True)
        self.assertRaises(TypeError, DebugMatchContext, {"id": "path"})
        self.assertRaises(TypeError, DebugMatchContext, ["path"])
        self.assertRaises(TypeError, DebugMatchContext, [])
        self.assertRaises(TypeError, DebugMatchContext, ())
        self.assertRaises(TypeError, DebugMatchContext, set())

    def test6_debug_match_context_update_input_validation(self):
        """Check if input is validated for DebugMatchContext.update()."""
        data = b"this is an example of a log line."
        match_context = MatchContext(data)
        self.assertRaises(TypeError, match_context.update, None)
        self.assertRaises(TypeError, match_context.update, True)
        self.assertRaises(TypeError, match_context.update, 123)
        self.assertRaises(TypeError, match_context.update, 123.22)


if __name__ == "__main__":
    unittest.main()
