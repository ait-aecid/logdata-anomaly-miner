import unittest
from _io import StringIO
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from aminer.analysis.Rules import EventGenerationMatchAction, \
  PathExistsMatchRule, ValueMatchRule, ValueListMatchRule, ValueRangeMatchRule, \
  StringRegexMatchRule, ModuloTimeMatchRule, ValueDependentModuloTimeMatchRule, \
  IPv4InRFC1918MatchRule, AndMatchRule, OrMatchRule, \
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

'''
NOTE: DebugMatchRule and DebugHistoryMatchRule are intentionally not tested, as there is not much to be tested.
ParallelMatchRule is also not tested as it is very similar to the OrMatchRule.
'''
class RuleTest(TestBase):
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
    
    '''
    This test case checks if events are generated and pushed to all event handlers.
    '''
    def test1event_generation_match_action(self):
      description = "Test1Rules"
      self.output_stream2 = StringIO()
      self.message = 'This message was generated, when the unit were successful.'
      
      self.match_context = MatchContext(b'25537')
      self.decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      self.match_element = self.decimal_integer_value_me.get_match_element('match', self.match_context)
      self.stream_printer_event_handler2 = StreamPrinterEventHandler(self.analysis_context, self.output_stream2)
      
      self.t = time()
      self.event_generation_match_action = EventGenerationMatchAction('Test.%s' % self.__class__.__name__,
        self.message, [self.stream_printer_event_handler, self.stream_printer_event_handler2])
      self.analysis_context.register_component(self.event_generation_match_action, description)
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), self.t, self.event_generation_match_action)
      self.event_generation_match_action.match_action(self.log_atom)
      
      self.assertEqual(self.output_stream.getvalue(), self.output_stream2.getvalue())
      self.assertEqual(self.output_stream.getvalue(), self.__expected_string
        % (datetime.fromtimestamp(self.t).strftime("%Y-%m-%d %H:%M:%S"),
        self.event_generation_match_action.__class__.__name__, description, 1,
        self.log_atom.parser_match.match_element.annotate_match('')))
    
    '''
    This test case proves the functionality of the AtomFilters
    '''
    def test2atom_filter_match_action(self):
      description = "Test2Rules"
      self.newMatchPathDetector = NewMatchPathDetector(self.aminer_config, [self.stream_printer_event_handler],
        'Default', False)
      self.logAtomFixedDME = LogAtom(self.fixed_dme.fixed_data, ParserMatch(self.match_element_fixed_dme), time(), self.newMatchPathDetector)
      self.subhandlerFilter = SubhandlerFilter([self.newMatchPathDetector])
      self.analysis_context.register_component(self.subhandlerFilter, description)
      self.analysis_context.register_component(self.newMatchPathDetector, description + "2")
      
      self.assertTrue(self.subhandlerFilter.receive_atom(self.logAtomFixedDME))
    
    '''
    This case unit the PathExistsMatchRule.
    '''
    def test3path_exists_match_rule(self):
      description = "Test3Rules"
      self.path_exists_match_rule = PathExistsMatchRule(self.match_s1, None)
      self.analysis_context.register_component(self.path_exists_match_rule, description)
      self.fixed_dme = FixedDataModelElement('s1', self.fixed_string)
      self.t = time()
            
      self.match_context = MatchContext(self.fixed_string)
      self.match_element = self.fixed_dme.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), self.t, self.path_exists_match_rule)
      
      self.assertTrue(self.path_exists_match_rule.match(self.log_atom))
      
      self.fixed_dme = FixedDataModelElement('s2', self.fixed_string)
      self.match_context = MatchContext(self.fixed_string)
      self.match_element = self.fixed_dme.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), self.t, self.path_exists_match_rule)
      
      self.assertTrue(not self.path_exists_match_rule.match(self.log_atom))
    
    '''
    This case unit the ValueMatchRule.
    '''
    def test4value_match_rule(self):
      description = "Test4Rules"
      self.value_match_rule = ValueMatchRule(self.match_s1, self.fixed_string, None)
      self.analysis_context.register_component(self.value_match_rule, description)
      self.fixed_dme = FixedDataModelElement('s1', self.fixed_string)
      
      self.match_context = MatchContext(self.fixed_string)
      self.match_element = self.fixed_dme.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_match_rule)
      self.assertTrue(self.value_match_rule.match(self.log_atom))
      
      self.fixed_dme = FixedDataModelElement('s1', b'another fixed String')
      self.match_context = MatchContext(b'another fixed String')
      self.match_element = self.fixed_dme.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_match_rule)
      self.assertTrue(not self.value_match_rule.match(self.log_atom))
    
    '''
    This case unit the ValueListMatchRule.
    '''
    def test5value_list_match_rule(self):
      description = "Test5Rules"
      self.value_list_match_rule = ValueListMatchRule('match/d1', [1, 2, 4, 8, 16, 32, 64, 128, 256, 512], None)
      self.analysis_context.register_component(self.value_list_match_rule, description)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
            
      self.match_context = MatchContext(b'64')
      self.match_element = self.decimal_integer_value_me.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_list_match_rule)
      self.assertTrue(self.value_list_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'4711')
      self.match_element = self.decimal_integer_value_me.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_list_match_rule)
      self.assertTrue(not self.value_list_match_rule.match(self.log_atom))
    
    '''
    This case unit the ValueRangeMatchRule.
    '''
    def test6value_range_match_rule(self):
      description = "Test6Rules"
      self.value_range_match_rule = ValueRangeMatchRule('match/d1', 1, 1000, None)
      self.analysis_context.register_component(self.value_range_match_rule, description)
      self.decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
          DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      
      self.match_context = MatchContext(b'1')
      self.match_element = self.decimal_integer_value_me.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_range_match_rule)
      self.assertTrue(self.value_range_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'1000')
      self.match_element = self.decimal_integer_value_me.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_range_match_rule)
      self.assertTrue(self.value_range_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'0')
      self.match_element = self.decimal_integer_value_me.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_range_match_rule)
      self.assertTrue(not self.value_range_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'1001')
      self.match_element = self.decimal_integer_value_me.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_range_match_rule)
      self.assertTrue(not self.value_range_match_rule.match(self.log_atom))
    
    '''
    This case unit the StringRegexMatchRule.
    '''
    def test7string_regex_match_rule(self):
      description = "Test7Rules"
      self.string_regex_match_rule = StringRegexMatchRule(self.match_any, re.compile('\w'), None)
      self.analysis_context.register_component(self.string_regex_match_rule, description)
      self.any_byte_date_me = AnyByteDataModelElement('any')
            
      self.match_context = MatchContext(self.alphabet)
      self.match_element = self.any_byte_date_me.get_match_element('match', self.match_context)
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.string_regex_match_rule)
      self.assertTrue(self.string_regex_match_rule.match(self.log_atom))

      self.match_context = MatchContext('--> There are 26 letters in the english alphabet')
      self.match_element = self.any_byte_date_me.get_match_element('match', self.match_context)
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.string_regex_match_rule)
      self.assertTrue(not self.string_regex_match_rule.match(self.log_atom))
    
    '''
    This case unit the ModuloTimeMatchRule.
    '''
    def test8modulo_time_match_rule(self):
      description = "Test8Rules"
      self.modulo_time_match_rule = ModuloTimeMatchRule(self.model_syslog_time, 86400, 43200, 86400, None)
      self.analysis_context.register_component(self.modulo_time_match_rule, description)
      self.date_time_model_element = DateTimeModelElement('time', b'%d.%m.%Y %H:%M:%S')
      
      self.match_context = MatchContext(b'14.02.2019 13:00:00')
      self.match_element = self.date_time_model_element.get_match_element(self.model_syslog, self.match_context)
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.date_time_model_element)
      self.assertTrue(self.modulo_time_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'15.02.2019 00:00:00')
      self.match_element = self.date_time_model_element.get_match_element(self.model_syslog, self.match_context)
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.date_time_model_element)
      self.assertTrue(not self.modulo_time_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'14.02.2019 12:00:00')
      self.match_element = self.date_time_model_element.get_match_element(self.model_syslog, self.match_context)
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.date_time_model_element)
      self.assertTrue(self.modulo_time_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'15.02.2019 01:00:00')
      self.match_element = self.date_time_model_element.get_match_element(self.model_syslog, self.match_context)
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.date_time_model_element)
      self.assertTrue(not self.modulo_time_match_rule.match(self.log_atom))
    
    '''
    This case unit the ValueDependentModuloTimeMatchRule. Limit look up not working with tuples.
    '''
    def test9value_dependent_modulo_time_match_rule(self):
      description = "Test9Rules"
      self.value_dependent_modulo_time_match_rule = ValueDependentModuloTimeMatchRule(self.model_syslog_time,
          86400, [self.model_syslog_time], {1550145600:[43200, 86400]})
      self.analysis_context.register_component(self.value_dependent_modulo_time_match_rule, description)
      self.date_time_model_element = DateTimeModelElement('time', b'%d.%m.%Y %H:%M:%S')
      
      self.match_context = MatchContext(b'14.02.2019 12:00:00')
      self.match_element = self.date_time_model_element.get_match_element(self.model_syslog, self.match_context)
      print(self.match_element.get_match_object())
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1550138400, self.date_time_model_element)
      self.assertTrue(self.value_dependent_modulo_time_match_rule.match(self.log_atom))
    
    '''
    This case unit the ValueDependentModuloTimeMatchRule.
    '''
    def test10ipv4_in_rfc1918_match_rule(self):
      description = "Test10Rules"
      self.i_pv4_in_rfc1918_match_rule = IPv4InRFC1918MatchRule(self.match_ipv4)
      self.analysis_context.register_component(self.i_pv4_in_rfc1918_match_rule, description)
      self.ip_address_data_model_element = IpAddressDataModelElement('IPv4');
      
      # private addresses
      self.match_context = MatchContext(b'192.168.0.0');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'192.168.255.255');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'172.16.0.0');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'172.31.255.255');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'10.0.0.0');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'10.255.255.255');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
      
      # public addresses
      self.match_context = MatchContext(b'192.167.255.255');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(not self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'192.169.0.0');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(not self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'172.15.255.255');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(not self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(not self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'172.32.0.0');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(not self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'9.255.255.255');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(not self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'11.0.0.0');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.i_pv4_in_rfc1918_match_rule)
      self.assertTrue(not self.i_pv4_in_rfc1918_match_rule.match(self.log_atom))
    
    '''
    This case unit the AndMatchRule.
    '''
    def test11and_match_rule(self):
      description = "Test11Rules"
      self.path_exists_match_rule = PathExistsMatchRule(self.match_ipv4, None)
      self.analysis_context.register_component(self.path_exists_match_rule, description)
      self.i_pv4_in_rfc1918_match_rule = IPv4InRFC1918MatchRule(self.match_ipv4)
      self.analysis_context.register_component(self.i_pv4_in_rfc1918_match_rule, description + "2")
      self.and_match_rule = AndMatchRule([self.path_exists_match_rule, self.i_pv4_in_rfc1918_match_rule])
      self.analysis_context.register_component(self.and_match_rule, description + "3")
      self.ip_address_data_model_element = IpAddressDataModelElement('IPv4');
      
      self.match_context = MatchContext(b'192.168.0.0');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.and_match_rule)
      self.assertTrue(self.and_match_rule.match(self.log_atom))
      
      # changing to IPv6
      self.path_exists_match_rule = PathExistsMatchRule('match/IPv6', None)
      self.and_match_rule = AndMatchRule([self.path_exists_match_rule, self.i_pv4_in_rfc1918_match_rule])
      self.match_context = MatchContext(b'192.168.0.0');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.and_match_rule)
      self.assertTrue(not self.and_match_rule.match(self.log_atom))
    
    '''
    This case unit the OrMatchRule.
    '''
    def test12or_match_rule(self):
      description = "Test12Rules"
      self.path_exists_match_rule = PathExistsMatchRule(self.match_ipv4, None)
      self.analysis_context.register_component(self.path_exists_match_rule, description)
      self.i_pv4_in_rfc1918_match_rule = IPv4InRFC1918MatchRule(self.match_ipv4)
      self.analysis_context.register_component(self.i_pv4_in_rfc1918_match_rule, description + "2")
      self.or_match_rule = OrMatchRule([self.path_exists_match_rule, self.i_pv4_in_rfc1918_match_rule])
      self.analysis_context.register_component(self.or_match_rule, description + "3")
      self.ip_address_data_model_element = IpAddressDataModelElement('IPv4');
      
      self.match_context = MatchContext(b'192.168.0.0');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.or_match_rule)
      self.assertTrue(self.or_match_rule.match(self.log_atom))
      
      # changing to IPv6
      self.path_exists_match_rule = PathExistsMatchRule('match/IPv6', None)
      self.or_match_rule = OrMatchRule([self.path_exists_match_rule, self.i_pv4_in_rfc1918_match_rule])
      self.match_context = MatchContext(b'192.168.0.0');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), time(), self.or_match_rule)
      self.assertTrue(self.or_match_rule.match(self.log_atom))
    
    '''
    This case unit the ValueDependentDelegatedMatchRule.
    '''
    def test13value_dependent_delegated_match_rule(self):
      description = "Test13Rules"
      self.string_regex_match_rule = StringRegexMatchRule(self.match_any, re.compile('\w'), None)
      self.analysis_context.register_component(self.string_regex_match_rule, description)
      self.any_byte_date_me = AnyByteDataModelElement('any')
      
      self.i_pv4_in_rfc1918_match_rule = IPv4InRFC1918MatchRule(self.match_ipv4)
      self.analysis_context.register_component(self.i_pv4_in_rfc1918_match_rule, description + "2")
      self.ip_address_data_model_element = IpAddressDataModelElement('IPv4');
      
      self.value_dependent_delegated_match_rule = ValueDependentDelegatedMatchRule([self.match_any, self.match_ipv4],
          {tuple([self.alphabet, None]):self.string_regex_match_rule,
           tuple([None, 3232235520]):self.i_pv4_in_rfc1918_match_rule})
      self.analysis_context.register_component(self.value_dependent_delegated_match_rule, description + "3")
      
      self.match_context = MatchContext(self.alphabet)
      self.match_element = self.any_byte_date_me.get_match_element('match', self.match_context)
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_dependent_delegated_match_rule)
      self.assertTrue(self.value_dependent_delegated_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'192.168.0.0');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_dependent_delegated_match_rule)
      self.assertTrue(self.value_dependent_delegated_match_rule.match(self.log_atom))
      
      # not matching values
      self.match_context = MatchContext('.There are 26 letters in the english alphabet')
      self.match_element = self.any_byte_date_me.get_match_element('match', self.match_context)
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_dependent_delegated_match_rule)
      self.assertTrue(not self.value_dependent_delegated_match_rule.match(self.log_atom))
      
      self.match_context = MatchContext(b'192.168.0.1');
      self.match_element = self.ip_address_data_model_element.get_match_element('match', self.match_context);
      self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.value_dependent_delegated_match_rule)
      self.assertTrue(not self.value_dependent_delegated_match_rule.match(self.log_atom))
    
    '''
    This case unit the NegationMatchRule.
    '''
    def test14negation_match_rule(self):
      description = "Test14Rules"
      self.path_exists_match_rule = PathExistsMatchRule(self.match_s1, None)
      self.analysis_context.register_component(self.path_exists_match_rule, description)
      self.negation_match_rule = NegationMatchRule(self.path_exists_match_rule)
      self.analysis_context.register_component(self.negation_match_rule, description + "2")
      self.fixed_dme = FixedDataModelElement('s1', self.fixed_string)
            
      self.match_context = MatchContext(self.fixed_string)
      self.match_element = self.fixed_dme.get_match_element('match', self.match_context)
      self.log_atom = self.log_atom = LogAtom(self.match_context.match_data, ParserMatch(self.match_element), 1, self.path_exists_match_rule)
      self.assertTrue(self.path_exists_match_rule.match(self.log_atom))
      self.assertTrue(not self.negation_match_rule.match(self.log_atom))


if __name__ == "__main__":
    unittest.main()
