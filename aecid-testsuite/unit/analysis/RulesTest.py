import unittest
import math
from aminer.analysis.Rules import EventGenerationMatchAction, AtomFilterMatchAction, PathExistsMatchRule, ValueMatchRule, ValueListMatchRule, \
    ValueRangeMatchRule, StringRegexMatchRule, ModuloTimeMatchRule, ValueDependentModuloTimeMatchRule, IPv4InRFC1918MatchRule, \
    AndMatchRule, OrMatchRule, ParallelMatchRule, ValueDependentDelegatedMatchRule, NegationMatchRule
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
import re
from aminer.parsing.MatchElement import MatchElement
from time import time
from unit.TestBase import TestBase, DummyMatchContext, DummyFixedDataModelElement, DummyNumberModelElement
from datetime import datetime, timezone


class RuleTest(TestBase):
    """NOTE: DebugMatchRule and DebugHistoryMatchRule are intentionally not tested, as there is not much to be tested."""
    def test1EventGenerationMatchAction(self):
        """This test case checks if events are generated and pushed to all event handlers."""
        expected_string = '%s This message was generated, when the unittest was successful.\n%s: "None" (%d lines)\n  %s\n\n'
        message = "This message was generated, when the unittest was successful."
        t = time()
        match_context = DummyMatchContext(b"25000")
        fdme = DummyFixedDataModelElement("s1", b"250")
        match_element = fdme.get_match_element("fixed", match_context)
        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, message, [self.stream_printer_event_handler])
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, egma)
        egma.match_action(log_atom)
        self.assertEqual(self.output_stream.getvalue(), expected_string % (
          datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), egma.__class__.__name__, 1, log_atom.parser_match.match_element.annotate_match("")))

        self.assertRaises(ValueError, EventGenerationMatchAction, "", message, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, b"Test", message, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, 123, message, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, 123.2, message, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, True, message, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, None, message, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, {"id": "Default"}, message, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, ["Test.%s" % self.__class__.__name__], message, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, (), message, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, set(), message, [self.stream_printer_event_handler])

        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", message.encode(), [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", 123, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", 123.2, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", True, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", None, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", {"id": "Default"}, [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", [message], [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", (), [self.stream_printer_event_handler])
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", set(), [self.stream_printer_event_handler])
        EventGenerationMatchAction("Test", "", [self.stream_printer_event_handler])

        self.assertRaises(ValueError, EventGenerationMatchAction, "Test", message, [])
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", message, ["default"])
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", message, None)
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", message, "")
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", message, b"Default")
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", message, True)
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", message, 123)
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", message, 123.3)
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", message, {"id": "Default"})
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", message, set())
        self.assertRaises(TypeError, EventGenerationMatchAction, "Test", message, ())

    def test2AtomFilterMatchAction(self):
        """This test case proves the functionality of the AtomFilterMatchAction."""
        t = time()
        match_context = DummyMatchContext(b"25000")
        fdme = DummyFixedDataModelElement("s1", b"25000")
        match_element = fdme.get_match_element("fixed", match_context)
        nmpd = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], "Default", False)
        afma = AtomFilterMatchAction([nmpd], True)
        log_atom = LogAtom(fdme.data, ParserMatch(match_element), t, afma)
        self.assertTrue(afma.match_action(log_atom))

        self.assertRaises(TypeError, AtomFilterMatchAction, "", True)
        self.assertRaises(TypeError, AtomFilterMatchAction, ["default"], True)
        self.assertRaises(TypeError, AtomFilterMatchAction, True, True)
        self.assertRaises(TypeError, AtomFilterMatchAction, b"Default", True)
        self.assertRaises(TypeError, AtomFilterMatchAction, 123, True)
        self.assertRaises(TypeError, AtomFilterMatchAction, 123.3, True)
        self.assertRaises(TypeError, AtomFilterMatchAction, {"id": "Default"}, True)
        self.assertRaises(TypeError, AtomFilterMatchAction, set(), True)
        self.assertRaises(TypeError, AtomFilterMatchAction, (), True)
        AtomFilterMatchAction([], True)
        AtomFilterMatchAction(None, True)

        self.assertRaises(TypeError, AtomFilterMatchAction, [nmpd], b"True")
        self.assertRaises(TypeError, AtomFilterMatchAction, [nmpd], "True")
        self.assertRaises(TypeError, AtomFilterMatchAction, [nmpd], 123)
        self.assertRaises(TypeError, AtomFilterMatchAction, [nmpd], 123.22)
        self.assertRaises(TypeError, AtomFilterMatchAction, [nmpd], {"id": "Default"})
        self.assertRaises(TypeError, AtomFilterMatchAction, [nmpd], ["Default"])
        self.assertRaises(TypeError, AtomFilterMatchAction, [nmpd], [])
        self.assertRaises(TypeError, AtomFilterMatchAction, [nmpd], ())
        self.assertRaises(TypeError, AtomFilterMatchAction, [nmpd], set())

    def test3AndMatchRule(self):
        """Test the AndMatchRule."""
        t = time()
        match_ipv4 = "match/IPv4"
        pemr_ipv4 = PathExistsMatchRule(match_ipv4, None)
        pemr_ipv6 = PathExistsMatchRule("match/IPv6", None)
        ipv4mr = IPv4InRFC1918MatchRule(match_ipv4)
        amr = AndMatchRule([pemr_ipv4, ipv4mr])
        fdme_v4 = DummyFixedDataModelElement("IPv4", b"192.168.0.0")
        fdme_v6 = DummyFixedDataModelElement("IPv6", b"2001:4860:4860::8888")

        match_context = DummyMatchContext(b"192.168.0.0")
        match_element = fdme_v4.get_match_element("match", match_context)
        match_element.match_object = 3232235520
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, amr)
        self.assertTrue(amr.match(log_atom))

        amr = AndMatchRule([pemr_ipv6, ipv4mr])
        match_context = DummyMatchContext(b"192.168.0.0")
        match_element = fdme_v4.get_match_element("match", match_context)
        match_element.match_object = 3232235520
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, amr)
        self.assertFalse(amr.match(log_atom))

        amr = AndMatchRule([pemr_ipv6, ipv4mr])
        match_context = DummyMatchContext(b"2001:4860:4860::8888")
        match_element = fdme_v6.get_match_element("match", match_context)
        match_element.match_object = 301989888
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, amr)
        self.assertFalse(amr.match(log_atom))

        amr = AndMatchRule([pemr_ipv4, ipv4mr])
        match_context = DummyMatchContext(b"2001:4860:4860::8888")
        match_element = fdme_v6.get_match_element("match", match_context)
        match_element.match_object = 301989888
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, amr)
        self.assertFalse(amr.match(log_atom))

        self.assertRaises(ValueError, AndMatchRule, [pemr_ipv6])
        self.assertRaises(ValueError, AndMatchRule, [])
        self.assertRaises(TypeError, AndMatchRule, ["default"])
        self.assertRaises(TypeError, AndMatchRule, "default")
        self.assertRaises(TypeError, AndMatchRule, b"default")
        self.assertRaises(TypeError, AndMatchRule, True)
        self.assertRaises(TypeError, AndMatchRule, 123)
        self.assertRaises(TypeError, AndMatchRule, 123.22)
        self.assertRaises(TypeError, AndMatchRule, {"id": "Default"})
        self.assertRaises(TypeError, AndMatchRule, ())
        self.assertRaises(TypeError, AndMatchRule, set())
        self.assertRaises(TypeError, AndMatchRule, None)

        self.assertRaises(TypeError, AndMatchRule, [pemr_ipv6, ipv4mr], b"True")
        self.assertRaises(TypeError, AndMatchRule, [pemr_ipv6, ipv4mr], "True")
        self.assertRaises(TypeError, AndMatchRule, [pemr_ipv6, ipv4mr], 123)
        self.assertRaises(TypeError, AndMatchRule, [pemr_ipv6, ipv4mr], 123.22)
        self.assertRaises(TypeError, AndMatchRule, [pemr_ipv6, ipv4mr], {"id": "Default"})
        self.assertRaises(TypeError, AndMatchRule, [pemr_ipv6, ipv4mr], ["Default"])
        self.assertRaises(TypeError, AndMatchRule, [pemr_ipv6, ipv4mr], [])
        self.assertRaises(TypeError, AndMatchRule, [pemr_ipv6, ipv4mr], ())
        self.assertRaises(TypeError, AndMatchRule, [pemr_ipv6, ipv4mr], set())

        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, "", [self.stream_printer_event_handler])
        AndMatchRule([pemr_ipv6, ipv4mr], egma)

    def test4OrMatchRule(self):
        """Test the OrMatchRule."""
        t = time()
        match_ipv4 = "match/IPv4"
        pemr_ipv4 = PathExistsMatchRule(match_ipv4, None)
        pemr_ipv6 = PathExistsMatchRule("match/IPv6", None)
        ipv4mr = IPv4InRFC1918MatchRule(match_ipv4)
        omr = OrMatchRule([pemr_ipv4, ipv4mr])
        fdme_v4 = DummyFixedDataModelElement("IPv4", b"192.168.0.0")
        fdme_v6 = DummyFixedDataModelElement("IPv6", b"2001:4860:4860::8888")

        match_context = DummyMatchContext(b"192.168.0.0")
        match_element = fdme_v4.get_match_element("match", match_context)
        match_element.match_object = 3232235520
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, omr)
        self.assertTrue(omr.match(log_atom))

        omr = OrMatchRule([pemr_ipv6, ipv4mr])
        match_context = DummyMatchContext(b"192.168.0.0")
        match_element = fdme_v4.get_match_element("match", match_context)
        match_element.match_object = 3232235520
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, omr)
        self.assertTrue(omr.match(log_atom))

        omr = OrMatchRule([pemr_ipv6, ipv4mr])
        match_context = DummyMatchContext(b"2001:4860:4860::8888")
        match_element = fdme_v6.get_match_element("match", match_context)
        match_element.match_object = 301989888
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, omr)
        self.assertTrue(omr.match(log_atom))

        omr = OrMatchRule([pemr_ipv4, ipv4mr])
        match_context = DummyMatchContext(b"2001:4860:4860::8888")
        match_element = fdme_v6.get_match_element("match", match_context)
        match_element.match_object = 301989888
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, omr)
        self.assertFalse(omr.match(log_atom))

        self.assertRaises(ValueError, OrMatchRule, [pemr_ipv6])
        self.assertRaises(ValueError, OrMatchRule, [])
        self.assertRaises(TypeError, OrMatchRule, ["default"])
        self.assertRaises(TypeError, OrMatchRule, "default")
        self.assertRaises(TypeError, OrMatchRule, b"default")
        self.assertRaises(TypeError, OrMatchRule, True)
        self.assertRaises(TypeError, OrMatchRule, 123)
        self.assertRaises(TypeError, OrMatchRule, 123.22)
        self.assertRaises(TypeError, OrMatchRule, {"id": "Default"})
        self.assertRaises(TypeError, OrMatchRule, ())
        self.assertRaises(TypeError, OrMatchRule, set())
        self.assertRaises(TypeError, OrMatchRule, None)

        self.assertRaises(TypeError, OrMatchRule, [pemr_ipv6, ipv4mr], b"True")
        self.assertRaises(TypeError, OrMatchRule, [pemr_ipv6, ipv4mr], "True")
        self.assertRaises(TypeError, OrMatchRule, [pemr_ipv6, ipv4mr], 123)
        self.assertRaises(TypeError, OrMatchRule, [pemr_ipv6, ipv4mr], 123.22)
        self.assertRaises(TypeError, OrMatchRule, [pemr_ipv6, ipv4mr], {"id": "Default"})
        self.assertRaises(TypeError, OrMatchRule, [pemr_ipv6, ipv4mr], ["Default"])
        self.assertRaises(TypeError, OrMatchRule, [pemr_ipv6, ipv4mr], [])
        self.assertRaises(TypeError, OrMatchRule, [pemr_ipv6, ipv4mr], ())
        self.assertRaises(TypeError, OrMatchRule, [pemr_ipv6, ipv4mr], set())

        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, "", [self.stream_printer_event_handler])
        OrMatchRule ([pemr_ipv6, ipv4mr], egma)

    def test5ParallelMatchRule(self):
        """Test the ParallelMatchRule."""
        t = time()
        match_ipv4 = "match/IPv4"
        pemr_ipv4 = PathExistsMatchRule(match_ipv4, None)
        pemr_ipv6 = PathExistsMatchRule("match/IPv6", None)
        ipv4mr = IPv4InRFC1918MatchRule(match_ipv4)
        omr = ParallelMatchRule([pemr_ipv4, ipv4mr])
        fdme_v4 = DummyFixedDataModelElement("IPv4", b"192.168.0.0")
        fdme_v6 = DummyFixedDataModelElement("IPv6", b"2001:4860:4860::8888")

        match_context = DummyMatchContext(b"192.168.0.0")
        match_element = fdme_v4.get_match_element("match", match_context)
        match_element.match_object = 3232235520
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, omr)
        self.assertTrue(omr.match(log_atom))

        omr = ParallelMatchRule([pemr_ipv6, ipv4mr])
        match_context = DummyMatchContext(b"192.168.0.0")
        match_element = fdme_v4.get_match_element("match", match_context)
        match_element.match_object = 3232235520
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, omr)
        self.assertTrue(omr.match(log_atom))

        omr = ParallelMatchRule([pemr_ipv6, ipv4mr])
        match_context = DummyMatchContext(b"2001:4860:4860::8888")
        match_element = fdme_v6.get_match_element("match", match_context)
        match_element.match_object = 301989888
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, omr)
        self.assertTrue(omr.match(log_atom))

        omr = ParallelMatchRule([pemr_ipv4, ipv4mr])
        match_context = DummyMatchContext(b"2001:4860:4860::8888")
        match_element = fdme_v6.get_match_element("match", match_context)
        match_element.match_object = 301989888
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, omr)
        self.assertFalse(omr.match(log_atom))

        self.assertRaises(ValueError, ParallelMatchRule, [pemr_ipv6])
        self.assertRaises(ValueError, ParallelMatchRule, [])
        self.assertRaises(TypeError, ParallelMatchRule, ["default"])
        self.assertRaises(TypeError, ParallelMatchRule, "default")
        self.assertRaises(TypeError, ParallelMatchRule, b"default")
        self.assertRaises(TypeError, ParallelMatchRule, True)
        self.assertRaises(TypeError, ParallelMatchRule, 123)
        self.assertRaises(TypeError, ParallelMatchRule, 123.22)
        self.assertRaises(TypeError, ParallelMatchRule, {"id": "Default"})
        self.assertRaises(TypeError, ParallelMatchRule, ())
        self.assertRaises(TypeError, ParallelMatchRule, set())
        self.assertRaises(TypeError, ParallelMatchRule, None)

        self.assertRaises(TypeError, ParallelMatchRule, [pemr_ipv6, ipv4mr], b"True")
        self.assertRaises(TypeError, ParallelMatchRule, [pemr_ipv6, ipv4mr], "True")
        self.assertRaises(TypeError, ParallelMatchRule, [pemr_ipv6, ipv4mr], 123)
        self.assertRaises(TypeError, ParallelMatchRule, [pemr_ipv6, ipv4mr], 123.22)
        self.assertRaises(TypeError, ParallelMatchRule, [pemr_ipv6, ipv4mr], {"id": "Default"})
        self.assertRaises(TypeError, ParallelMatchRule, [pemr_ipv6, ipv4mr], ["Default"])
        self.assertRaises(TypeError, ParallelMatchRule, [pemr_ipv6, ipv4mr], [])
        self.assertRaises(TypeError, ParallelMatchRule, [pemr_ipv6, ipv4mr], ())
        self.assertRaises(TypeError, ParallelMatchRule, [pemr_ipv6, ipv4mr], set())

        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, "", [self.stream_printer_event_handler])
        ParallelMatchRule([pemr_ipv6, ipv4mr], egma)

    def test6ValueDependentDelegatedMatchRule(self):
        """Test the ValueDependentDelegatedMatchRule."""
        match_any = "match/any"
        match_ipv4 = "match/IPv4"
        alphabet = b"There are 26 letters in the english alphabet"
        srmr = StringRegexMatchRule(match_any, re.compile(rb"\w"), None)
        fdme1 = DummyFixedDataModelElement("any", alphabet)
        fdme2 = DummyFixedDataModelElement("any", b".There are 26 letters in the english alphabet")

        ipv4mr = IPv4InRFC1918MatchRule(match_ipv4)
        fdme3 = DummyFixedDataModelElement("IPv4", b"192.168.0.0")
        fdme4 = DummyFixedDataModelElement("IPv4", b"192.168.0.1")

        vddmr = ValueDependentDelegatedMatchRule([match_any, match_ipv4], {(alphabet,): srmr, (3232235520,): ipv4mr})

        match_context = DummyMatchContext(alphabet)
        match_element = fdme1.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vddmr)
        self.assertTrue(vddmr.match(log_atom))

        match_context = DummyMatchContext(b"192.168.0.0")
        match_element = fdme3.get_match_element("match", match_context)
        match_element.match_object = 3232235520
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vddmr)
        self.assertTrue(vddmr.match(log_atom))

        match_context = DummyMatchContext(b".There are 26 letters in the english alphabet")
        match_element = fdme2.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vddmr)
        self.assertFalse(vddmr.match(log_atom))

        match_context = DummyMatchContext(b"192.168.0.1")
        match_element = fdme4.get_match_element("match", match_context)
        match_element.match_object = 3232235521
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vddmr)
        self.assertFalse(vddmr.match(log_atom))

        self.assertRaises(ValueError, ValueDependentDelegatedMatchRule, [], {(alphabet,): srmr})
        self.assertRaises(ValueError, ValueDependentDelegatedMatchRule, [""], {(alphabet,): srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, [srmr], {(alphabet,): srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, [b"default"], {(alphabet,): srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, "default", {(alphabet,): srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, b"default", {(alphabet,): srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, True, {(alphabet,): srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, 123, {(alphabet,): srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, 123.22, {(alphabet,): srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, {"id": "Default"}, {(alphabet,): srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, (), {(alphabet,): srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, set(), {(alphabet,): srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, None, {(alphabet,): srmr})

        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {"default": srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {True: srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {123: srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {123.22: srmr})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(): srmr})
        ValueDependentDelegatedMatchRule(["default"], {("default",): srmr})
        ValueDependentDelegatedMatchRule(["default"], {(b"default",): srmr})
        ValueDependentDelegatedMatchRule(["default"], {(123,): srmr})
        ValueDependentDelegatedMatchRule(["default"], {(123.2,): srmr})
        ValueDependentDelegatedMatchRule(["default"], {(True,): srmr})

        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, default_rule=b"default")
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, default_rule="default")
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, default_rule=True)
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, default_rule=123)
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, default_rule=123.3)
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, default_rule={"id": "Default"})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, default_rule=())
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, default_rule=set())
        ValueDependentDelegatedMatchRule(["default"], {("default",): srmr}, default_rule=srmr)

        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, match_action=b"default")
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, match_action="default")
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, match_action=True)
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, match_action=123)
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, match_action=123.3)
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, match_action={"id": "Default"})
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, match_action=())
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, match_action=[])
        self.assertRaises(TypeError, ValueDependentDelegatedMatchRule, ["default"], {(alphabet,): srmr}, match_action=set())
        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, "", [self.stream_printer_event_handler])
        ValueDependentDelegatedMatchRule(["default"], {("default",): srmr}, match_action=egma)

    def test7NegationMatchRule(self):
        """This case unit the NegationMatchRule."""
        match_s1 = "match/s1"
        fixed_string = b"fixed String"
        pemr = PathExistsMatchRule(match_s1, None)
        nmr = NegationMatchRule(pemr)
        fdme = DummyFixedDataModelElement("s1", fixed_string)

        match_context = DummyMatchContext(fixed_string)
        match_element = fdme.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, pemr)
        self.assertTrue(pemr.match(log_atom))
        self.assertFalse(nmr.match(log_atom))

        self.assertRaises(TypeError, NegationMatchRule, b"default")
        self.assertRaises(TypeError, NegationMatchRule, "default")
        self.assertRaises(TypeError, NegationMatchRule, True)
        self.assertRaises(TypeError, NegationMatchRule, 123)
        self.assertRaises(TypeError, NegationMatchRule, 123.3)
        self.assertRaises(TypeError, NegationMatchRule, {"id": "Default"})
        self.assertRaises(TypeError, NegationMatchRule, ())
        self.assertRaises(TypeError, NegationMatchRule, [])
        self.assertRaises(TypeError, NegationMatchRule, set())
        self.assertRaises(TypeError, NegationMatchRule, None)

        self.assertRaises(TypeError, NegationMatchRule, pemr, match_action=b"default")
        self.assertRaises(TypeError, NegationMatchRule, pemr, match_action="default")
        self.assertRaises(TypeError, NegationMatchRule, pemr, match_action=True)
        self.assertRaises(TypeError, NegationMatchRule, pemr, match_action=123)
        self.assertRaises(TypeError, NegationMatchRule, pemr, match_action=123.3)
        self.assertRaises(TypeError, NegationMatchRule, pemr, match_action={"id": "Default"})
        self.assertRaises(TypeError, NegationMatchRule, pemr, match_action=())
        self.assertRaises(TypeError, NegationMatchRule, pemr, match_action=set())
        self.assertRaises(TypeError, NegationMatchRule, pemr, match_action=[])

        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, "", [self.stream_printer_event_handler])
        NegationMatchRule(pemr, egma)

    def test8PathExistsMatchRule(self):
        """Test the PathExistsMatchRule."""
        t = time()
        match_s1 = "match/s1"
        data = b"fixed String"
        pemr = PathExistsMatchRule(match_s1, None)
        fdme1 = DummyFixedDataModelElement("s1", data)
        fdme2 = DummyFixedDataModelElement("s2", data)

        match_context = DummyMatchContext(data)
        match_element = fdme1.get_match_element("match", match_context)
        log_atom1 = LogAtom(match_context.match_data, ParserMatch(match_element), t, pemr)
        self.assertTrue(pemr.match(log_atom1))

        match_context = DummyMatchContext(data)
        match_element = fdme2.get_match_element("match", match_context)
        log_atom2 = LogAtom(match_context.match_data, ParserMatch(match_element), t, pemr)
        self.assertFalse(pemr.match(log_atom2))

        self.assertRaises(ValueError, PathExistsMatchRule, "")
        self.assertRaises(TypeError, PathExistsMatchRule, b"default")
        self.assertRaises(TypeError, PathExistsMatchRule, True)
        self.assertRaises(TypeError, PathExistsMatchRule, 123)
        self.assertRaises(TypeError, PathExistsMatchRule, 123.3)
        self.assertRaises(TypeError, PathExistsMatchRule, {"id": "Default"})
        self.assertRaises(TypeError, PathExistsMatchRule, ())
        self.assertRaises(TypeError, PathExistsMatchRule, [])
        self.assertRaises(TypeError, PathExistsMatchRule, set())
        self.assertRaises(TypeError, PathExistsMatchRule, None)

        self.assertRaises(TypeError, PathExistsMatchRule, "default", match_action=b"default")
        self.assertRaises(TypeError, PathExistsMatchRule, "default", match_action="default")
        self.assertRaises(TypeError, PathExistsMatchRule, "default", match_action=True)
        self.assertRaises(TypeError, PathExistsMatchRule, "default", match_action=123)
        self.assertRaises(TypeError, PathExistsMatchRule, "default", match_action=123.3)
        self.assertRaises(TypeError, PathExistsMatchRule, "default", match_action={"id": "Default"})
        self.assertRaises(TypeError, PathExistsMatchRule, "default", match_action=())
        self.assertRaises(TypeError, PathExistsMatchRule, "default", match_action=set())
        self.assertRaises(TypeError, PathExistsMatchRule, "default", match_action=[])
        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, "", [self.stream_printer_event_handler])
        PathExistsMatchRule("default", egma)

    def test9ValueMatchRule(self):
        """Test the ValueMatchRule."""
        data1 = b"fixed String"
        data2 = b"another fixed String"
        vmr = ValueMatchRule("match/s1", data1, None)
        fdme1 = DummyFixedDataModelElement("s1", data1)
        fdme2 = DummyFixedDataModelElement("s1", data2)

        match_context = DummyMatchContext(data1)
        match_element = fdme1.get_match_element("match", match_context)
        log_atom1 = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vmr)
        self.assertTrue(vmr.match(log_atom1))

        match_context = DummyMatchContext(data2)
        match_element = fdme2.get_match_element("match", match_context)
        log_atom2 = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vmr)
        self.assertFalse(vmr.match(log_atom2))

        self.assertRaises(ValueError, ValueMatchRule, "", b"value")
        self.assertRaises(TypeError, ValueMatchRule, b"default", b"value")
        self.assertRaises(TypeError, ValueMatchRule, True, b"value")
        self.assertRaises(TypeError, ValueMatchRule, 123, b"value")
        self.assertRaises(TypeError, ValueMatchRule, 123.3, b"value")
        self.assertRaises(TypeError, ValueMatchRule, {"id": "Default"}, b"value")
        self.assertRaises(TypeError, ValueMatchRule, (), b"value")
        self.assertRaises(TypeError, ValueMatchRule, [], b"value")
        self.assertRaises(TypeError, ValueMatchRule, set(), b"value")
        self.assertRaises(TypeError, ValueMatchRule, None, b"value")

        self.assertRaises(ValueError, ValueMatchRule, "default", b"")
        self.assertRaises(TypeError, ValueMatchRule, "default", b"value", match_action=b"default")
        self.assertRaises(TypeError, ValueMatchRule, "default", b"value", match_action="default")
        self.assertRaises(TypeError, ValueMatchRule, "default", b"value", match_action=True)
        self.assertRaises(TypeError, ValueMatchRule, "default", b"value", match_action=123)
        self.assertRaises(TypeError, ValueMatchRule, "default", b"value", match_action=123.3)
        self.assertRaises(TypeError, ValueMatchRule, "default", b"value", match_action={"id": "Default"})
        self.assertRaises(TypeError, ValueMatchRule, "default", b"value", match_action=())
        self.assertRaises(TypeError, ValueMatchRule, "default", b"value", match_action=set())
        self.assertRaises(TypeError, ValueMatchRule, "default", b"value", match_action=[])
        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, "", [self.stream_printer_event_handler])
        ValueMatchRule("default", b"value", egma)

    def test10ValueListMatchRule(self):
        """Test the ValueListMatchRule."""
        vlmr = ValueListMatchRule("match/d1", [1, 2, 4, 8, 16, 32, 64, 128, 256, 512], None)
        nme = DummyNumberModelElement("d1")

        match_context = DummyMatchContext(b"64")
        match_element = nme.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vlmr)
        self.assertTrue(vlmr.match(log_atom))

        match_context = DummyMatchContext(b"4711")
        match_element = nme.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vlmr)
        self.assertFalse(vlmr.match(log_atom))

        self.assertRaises(ValueError, ValueListMatchRule, "", [b"value"])
        self.assertRaises(TypeError, ValueListMatchRule, b"default", [b"value"])
        self.assertRaises(TypeError, ValueListMatchRule, True, [b"value"])
        self.assertRaises(TypeError, ValueListMatchRule, 123, [b"value"])
        self.assertRaises(TypeError, ValueListMatchRule, 123.3, [b"value"])
        self.assertRaises(TypeError, ValueListMatchRule, {"id": "Default"}, [b"value"])
        self.assertRaises(TypeError, ValueListMatchRule, (), [b"value"])
        self.assertRaises(TypeError, ValueListMatchRule, [], [b"value"])
        self.assertRaises(TypeError, ValueListMatchRule, set(), [b"value"])

        self.assertRaises(ValueError, ValueListMatchRule, "default", [])
        self.assertRaises(ValueError, ValueListMatchRule, "default", [""])
        self.assertRaises(TypeError, ValueListMatchRule, "default", b"default")
        self.assertRaises(TypeError, ValueListMatchRule, "default", "default")
        self.assertRaises(TypeError, ValueListMatchRule, "default", True)
        self.assertRaises(TypeError, ValueListMatchRule, "default", 123)
        self.assertRaises(TypeError, ValueListMatchRule, "default", 123.3)
        self.assertRaises(TypeError, ValueListMatchRule, "default", {"id": "Default"})
        self.assertRaises(TypeError, ValueListMatchRule, "default", ())
        self.assertRaises(TypeError, ValueListMatchRule, "default", set())

        self.assertRaises(TypeError, ValueListMatchRule, "default", [b"value"], match_action=b"default")
        self.assertRaises(TypeError, ValueListMatchRule, "default", [b"value"], match_action="default")
        self.assertRaises(TypeError, ValueListMatchRule, "default", [b"value"], match_action=True)
        self.assertRaises(TypeError, ValueListMatchRule, "default", [b"value"], match_action=123)
        self.assertRaises(TypeError, ValueListMatchRule, "default", [b"value"], match_action=123.3)
        self.assertRaises(TypeError, ValueListMatchRule, "default", [b"value"], match_action={"id": "Default"})
        self.assertRaises(TypeError, ValueListMatchRule, "default", [b"value"], match_action=())
        self.assertRaises(TypeError, ValueListMatchRule, "default", [b"value"], match_action=set())
        self.assertRaises(TypeError, ValueListMatchRule, "default", [b"value"], match_action=[])
        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, "", [self.stream_printer_event_handler])
        ValueListMatchRule("default", [b"value"], egma)

    def test11ValueRangeMatchRule(self):
        """Test the ValueRangeMatchRule."""
        vrmr = ValueRangeMatchRule("match/d1", 1, 1000, None)
        nme = DummyNumberModelElement("d1")

        match_context = DummyMatchContext(b"1")
        match_element = nme.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vrmr)
        self.assertTrue(vrmr.match(log_atom))

        match_context = DummyMatchContext(b"1000")
        match_element = nme.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vrmr)
        self.assertTrue(vrmr.match(log_atom))

        match_context = DummyMatchContext(b"0")
        match_element = nme.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vrmr)
        self.assertFalse(vrmr.match(log_atom))

        match_context = DummyMatchContext(b"1001")
        match_element = nme.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, vrmr)
        self.assertFalse(vrmr.match(log_atom))

        self.assertRaises(ValueError, ValueRangeMatchRule, "", 1, 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, b"default", 1, 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, True, 1, 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, 123, 1, 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, 123.3, 1, 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, {"id": "Default"}, 1, 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, (), 1, 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, [], 1, 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, set(), 1, 100)

        self.assertRaises(ValueError, ValueRangeMatchRule, "default", 100, 1)
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", [""], 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", b"default", 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", "default", 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", True, 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", {"id": "Default"}, 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", (), 100)
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", set(), 100)

        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, [""])
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, b"default")
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, "default")
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, True)
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, {"id": "Default"})
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, ())
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, set())

        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, 100, match_action=b"default")
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, 100, match_action="default")
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, 100, match_action=True)
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, 100, match_action=123)
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, 100, match_action=123.3)
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, 100, match_action={"id": "Default"})
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, 100, match_action=())
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, 100, match_action=set())
        self.assertRaises(TypeError, ValueRangeMatchRule, "default", 1, 100, match_action=[])

    def test12StringRegexMatchRule(self):
        """Test the StringRegexMatchRule."""
        match_any = "match/any"
        alphabet = b"There are 26 letters in the english alphabet"
        regex = re.compile(rb"\w")
        srmr = StringRegexMatchRule(match_any, regex, None)
        fdme1 = DummyFixedDataModelElement("any", alphabet)
        fdme2 = DummyFixedDataModelElement("any", b"--> There are 26 letters in the english alphabet")

        match_context = DummyMatchContext(alphabet)
        match_element = fdme1.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, srmr)
        self.assertTrue(srmr.match(log_atom))

        match_context = DummyMatchContext(b"--> There are 26 letters in the english alphabet")
        match_element = fdme2.get_match_element("match", match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, srmr)
        self.assertFalse(srmr.match(log_atom))

        self.assertRaises(ValueError, StringRegexMatchRule, "", regex)
        self.assertRaises(TypeError, StringRegexMatchRule, b"default", regex)
        self.assertRaises(TypeError, StringRegexMatchRule, True, regex)
        self.assertRaises(TypeError, StringRegexMatchRule, 123, regex)
        self.assertRaises(TypeError, StringRegexMatchRule, 123.3, regex)
        self.assertRaises(TypeError, StringRegexMatchRule, {"id": "Default"}, regex)
        self.assertRaises(TypeError, StringRegexMatchRule, (), regex)
        self.assertRaises(TypeError, StringRegexMatchRule, [], regex)
        self.assertRaises(TypeError, StringRegexMatchRule, set(), regex)
        self.assertRaises(TypeError, StringRegexMatchRule, None, regex)

        self.assertRaises(TypeError, StringRegexMatchRule, "default", None)
        self.assertRaises(TypeError, StringRegexMatchRule, "default", "default")
        self.assertRaises(TypeError, StringRegexMatchRule, "default", b"default")
        self.assertRaises(TypeError, StringRegexMatchRule, "default", True)
        self.assertRaises(TypeError, StringRegexMatchRule, "default", 123)
        self.assertRaises(TypeError, StringRegexMatchRule, "default", 123.3)
        self.assertRaises(TypeError, StringRegexMatchRule, "default", {"id": "Default"})
        self.assertRaises(TypeError, StringRegexMatchRule, "default", ())
        self.assertRaises(TypeError, StringRegexMatchRule, "default", [])
        self.assertRaises(TypeError, StringRegexMatchRule, "default", set())

        self.assertRaises(TypeError, ValueMatchRule, "default", regex, match_action=b"default")
        self.assertRaises(TypeError, ValueMatchRule, "default", regex, match_action="default")
        self.assertRaises(TypeError, ValueMatchRule, "default", regex, match_action=True)
        self.assertRaises(TypeError, ValueMatchRule, "default", regex, match_action=123)
        self.assertRaises(TypeError, ValueMatchRule, "default", regex, match_action=123.3)
        self.assertRaises(TypeError, ValueMatchRule, "default", regex, match_action={"id": "Default"})
        self.assertRaises(TypeError, ValueMatchRule, "default", regex, match_action=())
        self.assertRaises(TypeError, ValueMatchRule, "default", regex, match_action=set())
        self.assertRaises(TypeError, ValueMatchRule, "default", regex, match_action=[])
        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, "", [self.stream_printer_event_handler])
        ValueMatchRule("default", regex, egma)

    def test13ModuloTimeMatchRule(self):
        """Test the ModuloTimeMatchRule."""
        model_syslog_time = "/model/syslog/time"
        mtmr = ModuloTimeMatchRule(model_syslog_time, 86400, 43200, 86400, None)
        t = time()

        match_element = MatchElement(model_syslog_time, b"14.02.2019 13:00:00", 1550149200, None)
        log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, mtmr)
        self.assertTrue(mtmr.match(log_atom))

        match_element = MatchElement(model_syslog_time, b"15.02.2019 00:00:00", 1550188800, None)
        log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, mtmr)
        self.assertFalse(mtmr.match(log_atom))

        match_element = MatchElement(model_syslog_time, b"14.02.2019 12:00:00", 1550145600, None)
        log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, mtmr)
        self.assertTrue(mtmr.match(log_atom))

        match_element = MatchElement(model_syslog_time, b"15.02.2019 01:00:00", 1550192400, None)
        log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, mtmr)
        self.assertFalse(mtmr.match(log_atom))

        self.assertRaises(ValueError, ModuloTimeMatchRule, "", 86400, 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, b"default", 86400, 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, True, 86400, 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, 123, 86400, 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, 123.3, 86400, 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, {"id": "Default"}, 86400, 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, (), 86400, 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, [], 86400, 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, set(), 86400, 43200, 86400)

        self.assertRaises(ValueError, ModuloTimeMatchRule, "default", 0, 43200, 86400)
        self.assertRaises(ValueError, ModuloTimeMatchRule, "default", -1, 43200, 86400)
        self.assertRaises(ValueError, ModuloTimeMatchRule, "default", 86400, 86400, 43200)
        self.assertRaises(ValueError, ModuloTimeMatchRule, "default", 86400, 43200, 86401)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 1.1, 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", [""], 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", b"default", 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", "default", 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", True, 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", {"id": "Default"}, 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", (), 43200, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", set(), 43200, 86400)

        self.assertRaises(ValueError, ModuloTimeMatchRule, "default", 86400, -1, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 1.1, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, [""], 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, b"default", 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, "default", 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, True, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, {"id": "Default"}, 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, (), 86400)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, set(), 86400)

        self.assertRaises(ValueError, ModuloTimeMatchRule, "default", 86400, 43200, -1)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86399.1)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, [""])
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, b"default")
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, "default")
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, True)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, {"id": "Default"})
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, ())
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, set())

        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, match_action=b"default")
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, match_action="default")
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, match_action=True)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, match_action=123)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, match_action=123.3)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, match_action={"id": "Default"})
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, match_action=())
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, match_action=set())
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, match_action=[])

        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, tzinfo=b"default")
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, tzinfo="default")
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, tzinfo=True)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, tzinfo=123)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, tzinfo=123.3)
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, tzinfo={"id": "Default"})
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, tzinfo=())
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, tzinfo=set())
        self.assertRaises(TypeError, ModuloTimeMatchRule, "default", 86400, 43200, 86400, tzinfo=[])

        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, "", [self.stream_printer_event_handler])
        ModuloTimeMatchRule(model_syslog_time, 86400, 0, 75000, egma, datetime.now(timezone.utc).astimezone().tzinfo)

    def test14ValueDependentModuloTimeMatchRule(self):
        """Test the ValueDependentModuloTimeMatchRule."""
        model_syslog_time = "/model/syslog/time"
        vdmtmr1 = ValueDependentModuloTimeMatchRule(model_syslog_time, 86400, [model_syslog_time], {1550145600: [43200, 86400]})
        vdmtmr2 = ValueDependentModuloTimeMatchRule(model_syslog_time, 86400, [model_syslog_time], {1550145600: [40000, 86400]}, default_limit=[43200, 86400])
        t = time()

        match_element = MatchElement(model_syslog_time, b"14.02.2019 13:00:00", 1550149200, None)
        log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, vdmtmr1)
        self.assertFalse(vdmtmr1.match(log_atom))
        self.assertTrue(vdmtmr2.match(log_atom))

        match_element = MatchElement(model_syslog_time, b"15.02.2019 00:00:00", 1550188800, None)
        log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, vdmtmr1)
        self.assertFalse(vdmtmr1.match(log_atom))
        self.assertFalse(vdmtmr2.match(log_atom))

        match_element = MatchElement(model_syslog_time, b"14.02.2019 12:00:00", 1550145600, None)
        log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, vdmtmr1)
        self.assertTrue(vdmtmr1.match(log_atom))
        self.assertTrue(vdmtmr2.match(log_atom))

        match_element = MatchElement(model_syslog_time, b"15.02.2019 01:00:00", 1550192400, None)
        log_atom = LogAtom(match_element.match_string, ParserMatch(match_element), t, vdmtmr1)
        self.assertFalse(vdmtmr1.match(log_atom))
        self.assertFalse(vdmtmr2.match(log_atom))

        self.assertRaises(ValueError, ValueDependentModuloTimeMatchRule, "", 86400, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, b"default", 86400, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, True, 86400, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, 123, 86400, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, 123.3, 86400, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, {"id": "Default"}, 86400, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, (), 86400, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, [], 86400, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, set(), 86400, default_limit=[43200, 86400])

        self.assertRaises(ValueError, ValueDependentModuloTimeMatchRule, "default", 0, default_limit=[43200, 86400])
        self.assertRaises(ValueError, ValueDependentModuloTimeMatchRule, "default", -1, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 1.1, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", [""], default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", b"default", default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", "default", default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", True, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", {"id": "Default"}, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", (), default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", set(), default_limit=[43200, 86400])

        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=[""], default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=[b"default"], default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=[True], default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=[123], default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list={"id": "Default"}, default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=(), default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=set(), default_limit=[43200, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list="default", default_limit=[43200, 86400])

        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={1550145600: [86400, 43200]})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={1550145600: [43200, 86401]})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={1550145600: [43200]})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={1550145600: [43200, 86401, 1]})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={1550145600: (43200, 86401)})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={None: [43200, 86400]})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={1550145600: ["43200", 86400]})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={1550145600: [b"43200", 86400]})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={1550145600: [True, 86400]})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={1550145600: [{"id": "Default"}, 86400]})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={1550145600: [(43200,), 86400]})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, target_path_list=["default"], limit_lookup_dict={1550145600: [set(), 86400]})

        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[86400, 43200])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86401])
        self.assertRaises(ValueError, ValueDependentModuloTimeMatchRule, "default", 86400)
        self.assertRaises(ValueError, ValueDependentModuloTimeMatchRule, "default", 86400, [], {})
        self.assertRaises(ValueError, ValueDependentModuloTimeMatchRule, "default", 86400, None, None)
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=["43200", 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[b"43200", 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[True, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[{"id": "Default"}, 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[(43200,), 86400])
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[set(), 86400])

        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], match_action=b"default")
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], match_action="default")
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], match_action=True)
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], match_action=123)
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], match_action=123.3)
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], match_action={"id": "Default"})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], match_action=())
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], match_action=set())
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], match_action=[])

        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], tzinfo=b"default")
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], tzinfo="default")
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], tzinfo=True)
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], tzinfo=123)
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], tzinfo=123.3)
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], tzinfo={"id": "Default"})
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], tzinfo=())
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], tzinfo=set())
        self.assertRaises(TypeError, ValueDependentModuloTimeMatchRule, "default", 86400, default_limit=[43200, 86400], tzinfo=[])

        ValueDependentModuloTimeMatchRule(model_syslog_time, 86400, [model_syslog_time], {1550145600: [43200, 86400], 0: [1, 2]}, default_limit=[43200, 86400])
        ValueDependentModuloTimeMatchRule(model_syslog_time, 86400, [], {}, default_limit=[43200, 86400])
        ValueDependentModuloTimeMatchRule(model_syslog_time, 86400, None, None, default_limit=[43200, 86400])

    def test15IPv4InRFC1918MatchRule(self):
        """Test the IPv4InRFC1918MatchRule."""
        t = time()
        match_ipv4 = "match/IPv4"
        ipv4mr = IPv4InRFC1918MatchRule(match_ipv4)
        private_addresses = [b"192.168.0.0", b"192.168.255.255", b"172.16.0.0", b"172.31.255.255", b"10.0.0.0", b"10.255.255.255"]
        public_addresses = [b"192.167.255.255", b"192.169.0.0", b"172.15.255.255", b"172.32.0.0", b"9.255.255.255", b"11.0.0.0"]
        fdme1 = DummyFixedDataModelElement("IPv4", b"192.168.0.0")
        fdme2 = DummyFixedDataModelElement("IPv4", b"192.168.0.1")

        for ip in private_addresses:
            fdme = DummyFixedDataModelElement("IPv4", ip)
            match_context = DummyMatchContext(ip)
            match_element = fdme.get_match_element("match", match_context)
            x = [int(x.decode()) for x in ip.split(b".")]
            match_element.match_object = int(x[0] * math.pow(256, 3) + x[1] * math.pow(256, 2) + x[2] * math.pow(256, 1) + x[3])
            log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, ipv4mr)
            self.assertTrue(ipv4mr.match(log_atom))

        for ip in public_addresses:
            fdme = DummyFixedDataModelElement("IPv4", ip)
            match_context = DummyMatchContext(ip)
            match_element = fdme.get_match_element("match", match_context)
            x = [int(x.decode()) for x in ip.split(b".")]
            match_element.match_object = int(x[0] * math.pow(256, 3) + x[1] * math.pow(256, 2) + x[2] * math.pow(256, 1) + x[3])
            log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, ipv4mr)
            self.assertFalse(ipv4mr.match(log_atom))

        self.assertRaises(ValueError, IPv4InRFC1918MatchRule, "")
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, b"default")
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, True)
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, 123)
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, 123.3)
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, {"id": "Default"})
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, ())
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, [])
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, set())
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, None)

        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, "default", match_action=b"default")
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, "default", match_action="default")
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, "default", match_action=True)
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, "default", match_action=123)
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, "default", match_action=123.3)
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, "default", match_action={"id": "Default"})
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, "default", match_action=())
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, "default", match_action=set())
        self.assertRaises(TypeError, IPv4InRFC1918MatchRule, "default", match_action=[])
        egma = EventGenerationMatchAction("Test.%s" % self.__class__.__name__, "", [self.stream_printer_event_handler])
        IPv4InRFC1918MatchRule("default", egma)


if __name__ == "__main__":
    unittest.main()
