import unittest
from _io import StringIO
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from aminer.analysis.Rules import EventGenerationMatchAction, PathExistsMatchRule, ValueMatchRule, ValueListMatchRule, ValueRangeMatchRule, \
    StringRegexMatchRule, ModuloTimeMatchRule, ValueDependentModuloTimeMatchRule, IPv4InRFC1918MatchRule, AndMatchRule, OrMatchRule, \
    ValueDependentDelegatedMatchRule, NegationMatchRule
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.analysis.AtomFilters import SubhandlerFilter
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
import re
from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DateTimeModelElement import DateTimeModelElement
from time import time
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
from unit.TestBase import TestBase
from datetime import datetime


class RuleTest(TestBase):
    """NOTE: DebugMatchRule and DebugHistoryMatchRule are intentionally not tested, as there is not much to be tested. ParallelMatchRule is
    also not tested as it is very similar to the OrMatchRule. """
    __expected_string = '%s This message was generated, when the unit were successful.\n%s: "%s" (%d lines)\n  %s\n\n'

    match_s1 = 'match/s1'
    fixed_string = b'fixed String'
    match_any = 'match/any'
    alphabet = 'There are 26 letters in the english alphabet'
    model_syslog_time = '/model/syslog/time'
    model_syslog = '/model/syslog'
    match_ipv4 = 'match/IPv4'

    match_context_fixed_dme = MatchContext(b'25000')
    fixed_dme = FixedDataModelElement('s1', b'25000')
    match_element_fixed_dme = fixed_dme.get_match_element("fixed", match_context_fixed_dme)

    def test1event_generation_match_action(self):
        """This test case checks if events are generated and pushed to all event handlers."""
        description = "Test1Rules"
        output_stream2 = StringIO()
        message = 'This message was generated, when the unit were successful.'

        match_context = MatchContext(b'25537')
        decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                                   DecimalIntegerValueModelElement.PAD_TYPE_NONE)
        match_element = decimal_integer_value_me.get_match_element('match', match_context)
        stream_printer_event_handler2 = StreamPrinterEventHandler(self.analysis_context, output_stream2)

        t = time()
        event_generation_match_action = EventGenerationMatchAction('Test.%s' % self.__class__.__name__, message, [
            self.stream_printer_event_handler, stream_printer_event_handler2])
        self.analysis_context.register_component(event_generation_match_action, description)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, event_generation_match_action)
        event_generation_match_action.match_action(log_atom)

        self.assertEqual(self.output_stream.getvalue(), output_stream2.getvalue())
        self.assertEqual(self.output_stream.getvalue(), self.__expected_string % (
          datetime.fromtimestamp(t).strftime("%Y-%m-%d %H:%M:%S"), event_generation_match_action.__class__.__name__, description, 1,
          log_atom.parser_match.match_element.annotate_match('')))

    def test2atom_filter_match_action(self):
        """This test case proves the functionality of the AtomFilters"""
        description = "Test2Rules"
        newMatchPathDetector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler], 'Default', False)
        logAtomFixedDME = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), time(), newMatchPathDetector)
        subhandlerFilter = SubhandlerFilter([newMatchPathDetector])
        self.analysis_context.register_component(subhandlerFilter, description)
        self.analysis_context.register_component(newMatchPathDetector, description + "2")

        self.assertTrue(subhandlerFilter.receive_atom(logAtomFixedDME))

    def test3path_exists_match_rule(self):
        """This case unit the PathExistsMatchRule."""
        description = "Test3Rules"
        path_exists_match_rule = PathExistsMatchRule(self.match_s1, None)
        self.analysis_context.register_component(path_exists_match_rule, description)
        self.fixed_dme = FixedDataModelElement('s1', self.fixed_string)
        t = time()

        match_context = MatchContext(self.fixed_string)
        match_element = self.fixed_dme.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, path_exists_match_rule)

        self.assertTrue(path_exists_match_rule.match(log_atom))

        self.fixed_dme = FixedDataModelElement('s2', self.fixed_string)
        match_context = MatchContext(self.fixed_string)
        match_element = self.fixed_dme.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), t, path_exists_match_rule)

        self.assertTrue(not path_exists_match_rule.match(log_atom))

    def test4value_match_rule(self):
        """This case unit the ValueMatchRule."""
        description = "Test4Rules"
        value_match_rule = ValueMatchRule(self.match_s1, self.fixed_string, None)
        self.analysis_context.register_component(value_match_rule, description)
        self.fixed_dme = FixedDataModelElement('s1', self.fixed_string)

        match_context = MatchContext(self.fixed_string)
        match_element = self.fixed_dme.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_match_rule)
        self.assertTrue(value_match_rule.match(log_atom))

        self.fixed_dme = FixedDataModelElement('s1', b'another fixed String')
        match_context = MatchContext(b'another fixed String')
        match_element = self.fixed_dme.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_match_rule)
        self.assertTrue(not value_match_rule.match(log_atom))

    def test5value_list_match_rule(self):
        """This case unit the ValueListMatchRule."""
        description = "Test5Rules"
        value_list_match_rule = ValueListMatchRule('match/d1', [1, 2, 4, 8, 16, 32, 64, 128, 256, 512], None)
        self.analysis_context.register_component(value_list_match_rule, description)
        decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                                   DecimalIntegerValueModelElement.PAD_TYPE_NONE)

        match_context = MatchContext(b'64')
        match_element = decimal_integer_value_me.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_list_match_rule)
        self.assertTrue(value_list_match_rule.match(log_atom))

        match_context = MatchContext(b'4711')
        match_element = decimal_integer_value_me.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_list_match_rule)
        self.assertTrue(not value_list_match_rule.match(log_atom))

    def test6value_range_match_rule(self):
        """This case unit the ValueRangeMatchRule."""
        description = "Test6Rules"
        value_range_match_rule = ValueRangeMatchRule('match/d1', 1, 1000, None)
        self.analysis_context.register_component(value_range_match_rule, description)
        decimal_integer_value_me = DecimalIntegerValueModelElement('d1', DecimalIntegerValueModelElement.SIGN_TYPE_NONE,
                                                                   DecimalIntegerValueModelElement.PAD_TYPE_NONE)

        match_context = MatchContext(b'1')
        match_element = decimal_integer_value_me.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_range_match_rule)
        self.assertTrue(value_range_match_rule.match(log_atom))

        match_context = MatchContext(b'1000')
        match_element = decimal_integer_value_me.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_range_match_rule)
        self.assertTrue(value_range_match_rule.match(log_atom))

        match_context = MatchContext(b'0')
        match_element = decimal_integer_value_me.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_range_match_rule)
        self.assertTrue(not value_range_match_rule.match(log_atom))

        match_context = MatchContext(b'1001')
        match_element = decimal_integer_value_me.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_range_match_rule)
        self.assertTrue(not value_range_match_rule.match(log_atom))

    def test7string_regex_match_rule(self):
        """This case unit the StringRegexMatchRule."""
        description = "Test7Rules"
        string_regex_match_rule = StringRegexMatchRule(self.match_any, re.compile(r'\w'), None)
        self.analysis_context.register_component(string_regex_match_rule, description)
        any_byte_date_me = AnyByteDataModelElement('any')

        match_context = MatchContext(self.alphabet)
        match_element = any_byte_date_me.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, string_regex_match_rule)
        self.assertTrue(string_regex_match_rule.match(log_atom))

        match_context = MatchContext('--> There are 26 letters in the english alphabet')
        match_element = any_byte_date_me.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, string_regex_match_rule)
        self.assertTrue(not string_regex_match_rule.match(log_atom))

    def test8modulo_time_match_rule(self):
        """This case unit the ModuloTimeMatchRule."""
        description = "Test8Rules"
        modulo_time_match_rule = ModuloTimeMatchRule(self.model_syslog_time, 86400, 43200, 86400, None)
        self.analysis_context.register_component(modulo_time_match_rule, description)
        date_time_model_element = DateTimeModelElement('time', b'%d.%m.%Y %H:%M:%S')

        match_context = MatchContext(b'14.02.2019 13:00:00')
        match_element = date_time_model_element.get_match_element(self.model_syslog, match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), date_time_model_element)
        self.assertTrue(modulo_time_match_rule.match(log_atom))

        match_context = MatchContext(b'15.02.2019 00:00:00')
        match_element = date_time_model_element.get_match_element(self.model_syslog, match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), date_time_model_element)
        self.assertTrue(not modulo_time_match_rule.match(log_atom))

        match_context = MatchContext(b'14.02.2019 12:00:00')
        match_element = date_time_model_element.get_match_element(self.model_syslog, match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), date_time_model_element)
        self.assertTrue(modulo_time_match_rule.match(log_atom))

        match_context = MatchContext(b'15.02.2019 01:00:00')
        match_element = date_time_model_element.get_match_element(self.model_syslog, match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), date_time_model_element)
        self.assertTrue(not modulo_time_match_rule.match(log_atom))

    def test9value_dependent_modulo_time_match_rule(self):
        """This case unit the ValueDependentModuloTimeMatchRule. Limit look up not working with tuples."""
        description = "Test9Rules"
        value_dependent_modulo_time_match_rule = ValueDependentModuloTimeMatchRule(self.model_syslog_time, 86400, [self.model_syslog_time],
                                                                                   {1550145600: [43200, 86400]})
        self.analysis_context.register_component(value_dependent_modulo_time_match_rule, description)
        date_time_model_element = DateTimeModelElement('time', b'%d.%m.%Y %H:%M:%S')

        match_context = MatchContext(b'14.02.2019 12:00:00')
        match_element = date_time_model_element.get_match_element(self.model_syslog, match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1550138400, date_time_model_element)
        self.assertTrue(value_dependent_modulo_time_match_rule.match(log_atom))

    def test10ipv4_in_rfc1918_match_rule(self):
        """This case unit the ValueDependentModuloTimeMatchRule."""
        description = "Test10Rules"
        i_pv4_in_rfc1918_match_rule = IPv4InRFC1918MatchRule(self.match_ipv4)
        self.analysis_context.register_component(i_pv4_in_rfc1918_match_rule, description)
        ip_address_data_model_element = IpAddressDataModelElement('IPv4')

        # private addresses
        match_context = MatchContext(b'192.168.0.0')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(i_pv4_in_rfc1918_match_rule.match(log_atom))

        match_context = MatchContext(b'192.168.255.255')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(i_pv4_in_rfc1918_match_rule.match(log_atom))

        match_context = MatchContext(b'172.16.0.0')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(i_pv4_in_rfc1918_match_rule.match(log_atom))

        match_context = MatchContext(b'172.31.255.255')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(i_pv4_in_rfc1918_match_rule.match(log_atom))

        match_context = MatchContext(b'10.0.0.0')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(i_pv4_in_rfc1918_match_rule.match(log_atom))

        match_context = MatchContext(b'10.255.255.255')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(i_pv4_in_rfc1918_match_rule.match(log_atom))

        # public addresses
        match_context = MatchContext(b'192.167.255.255')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(not i_pv4_in_rfc1918_match_rule.match(log_atom))

        match_context = MatchContext(b'192.169.0.0')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(not i_pv4_in_rfc1918_match_rule.match(log_atom))

        match_context = MatchContext(b'172.15.255.255')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(not match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(not i_pv4_in_rfc1918_match_rule.match(log_atom))

        match_context = MatchContext(b'172.32.0.0')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(not i_pv4_in_rfc1918_match_rule.match(log_atom))

        match_context = MatchContext(b'9.255.255.255')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(not i_pv4_in_rfc1918_match_rule.match(log_atom))

        match_context = MatchContext(b'11.0.0.0')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), i_pv4_in_rfc1918_match_rule)
        self.assertTrue(not i_pv4_in_rfc1918_match_rule.match(log_atom))

    def test11and_match_rule(self):
        """This case unit the AndMatchRule."""
        description = "Test11Rules"
        path_exists_match_rule = PathExistsMatchRule(self.match_ipv4, None)
        self.analysis_context.register_component(path_exists_match_rule, description)
        i_pv4_in_rfc1918_match_rule = IPv4InRFC1918MatchRule(self.match_ipv4)
        self.analysis_context.register_component(i_pv4_in_rfc1918_match_rule, description + "2")
        and_match_rule = AndMatchRule([path_exists_match_rule, i_pv4_in_rfc1918_match_rule])
        self.analysis_context.register_component(and_match_rule, description + "3")
        ip_address_data_model_element = IpAddressDataModelElement('IPv4')

        match_context = MatchContext(b'192.168.0.0')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), and_match_rule)
        self.assertTrue(and_match_rule.match(log_atom))

        # changing to IPv6
        path_exists_match_rule = PathExistsMatchRule('match/IPv6', None)
        and_match_rule = AndMatchRule([path_exists_match_rule, i_pv4_in_rfc1918_match_rule])
        match_context = MatchContext(b'192.168.0.0')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), and_match_rule)
        self.assertTrue(not and_match_rule.match(log_atom))

    def test12or_match_rule(self):
        """This case unit the OrMatchRule."""
        description = "Test12Rules"
        path_exists_match_rule = PathExistsMatchRule(self.match_ipv4, None)
        self.analysis_context.register_component(path_exists_match_rule, description)
        i_pv4_in_rfc1918_match_rule = IPv4InRFC1918MatchRule(self.match_ipv4)
        self.analysis_context.register_component(i_pv4_in_rfc1918_match_rule, description + "2")
        or_match_rule = OrMatchRule([path_exists_match_rule, i_pv4_in_rfc1918_match_rule])
        self.analysis_context.register_component(or_match_rule, description + "3")
        ip_address_data_model_element = IpAddressDataModelElement('IPv4')

        match_context = MatchContext(b'192.168.0.0')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), or_match_rule)
        self.assertTrue(or_match_rule.match(log_atom))

        # changing to IPv6
        path_exists_match_rule = PathExistsMatchRule('match/IPv6', None)
        or_match_rule = OrMatchRule([path_exists_match_rule, i_pv4_in_rfc1918_match_rule])
        match_context = MatchContext(b'192.168.0.0')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), time(), or_match_rule)
        self.assertTrue(or_match_rule.match(log_atom))

    def test13value_dependent_delegated_match_rule(self):
        """This case unit the ValueDependentDelegatedMatchRule."""
        description = "Test13Rules"
        string_regex_match_rule = StringRegexMatchRule(self.match_any, re.compile(r'\w'), None)
        self.analysis_context.register_component(string_regex_match_rule, description)
        any_byte_date_me = AnyByteDataModelElement('any')

        i_pv4_in_rfc1918_match_rule = IPv4InRFC1918MatchRule(self.match_ipv4)
        self.analysis_context.register_component(i_pv4_in_rfc1918_match_rule, description + "2")
        ip_address_data_model_element = IpAddressDataModelElement('IPv4')

        value_dependent_delegated_match_rule = ValueDependentDelegatedMatchRule([
            self.match_any, self.match_ipv4], {(self.alphabet, None): string_regex_match_rule, 
                                               (None, 3232235520): i_pv4_in_rfc1918_match_rule})
        self.analysis_context.register_component(value_dependent_delegated_match_rule, description + "3")

        match_context = MatchContext(self.alphabet)
        match_element = any_byte_date_me.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_dependent_delegated_match_rule)
        self.assertTrue(value_dependent_delegated_match_rule.match(log_atom))

        match_context = MatchContext(b'192.168.0.0')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_dependent_delegated_match_rule)
        self.assertTrue(value_dependent_delegated_match_rule.match(log_atom))

        # not matching values
        match_context = MatchContext('.There are 26 letters in the english alphabet')
        match_element = any_byte_date_me.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_dependent_delegated_match_rule)
        self.assertTrue(not value_dependent_delegated_match_rule.match(log_atom))

        match_context = MatchContext(b'192.168.0.1')
        match_element = ip_address_data_model_element.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, value_dependent_delegated_match_rule)
        self.assertTrue(not value_dependent_delegated_match_rule.match(log_atom))

    def test14negation_match_rule(self):
        """This case unit the NegationMatchRule."""
        description = "Test14Rules"
        path_exists_match_rule = PathExistsMatchRule(self.match_s1, None)
        self.analysis_context.register_component(path_exists_match_rule, description)
        negation_match_rule = NegationMatchRule(path_exists_match_rule)
        self.analysis_context.register_component(negation_match_rule, description + "2")
        self.fixed_dme = FixedDataModelElement('s1', self.fixed_string)

        match_context = MatchContext(self.fixed_string)
        match_element = self.fixed_dme.get_match_element('match', match_context)
        log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, path_exists_match_rule)
        self.assertTrue(path_exists_match_rule.match(log_atom))
        self.assertTrue(not negation_match_rule.match(log_atom))


if __name__ == "__main__":
    unittest.main()
