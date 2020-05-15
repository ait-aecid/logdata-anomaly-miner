import unittest
from _io import BytesIO
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.analysis.MatchValueStreamWriter import MatchValueStreamWriter
from aminer.parsing.ParserMatch import ParserMatch
from aminer.input.LogAtom import LogAtom
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from unit.TestBase import TestBase


class MatchValueStreamWriterTest(TestBase):
    euro = b'Euro '
    match_sequence_s1 = 'match/sequence/s1'
    match_sequence_d1 = 'match/sequence/d1'

    '''
    This test case sets up a set of values, which are all expected to be matched.
    '''
    def test1all_atoms_match(self):
      description = "Test1MatchValueStreamWriter"
      output_stream = BytesIO()
      match_context = MatchContext(b'25537Euro 25538Euro 25539Euro 25540Euro ')
      decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
        DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      fixed_dme = FixedDataModelElement('s1', self.euro)
      sequence_model_element = SequenceModelElement('sequence', [decimal_integer_value_me, fixed_dme])
      match_value_stream_writer = MatchValueStreamWriter(output_stream, [self.match_sequence_d1, self.match_sequence_s1], b';', b'-')
      self.analysis_context.register_component(match_value_stream_writer, description)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)

      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      self.assertEqual(output_stream.getvalue().decode(), '25537;Euro \n25538;Euro \n25539;Euro \n25540;Euro \n')
    
    '''
    This test case sets up a set of values, which are all expected to be matched.
    The seperator string is None, so all values are expected to be one string.
    '''
    def test2all_atoms_match_no_seperator(self):
      description = "Test2MatchValueStreamWriter"
      output_stream = BytesIO()
      match_context = MatchContext(b'25537Euro 25538Euro 25539Euro 25540Euro ')
      decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
        DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      
      fixed_dme = FixedDataModelElement('s1', self.euro)
      sequence_model_element = SequenceModelElement('sequence', [decimal_integer_value_me, fixed_dme])
      match_value_stream_writer = MatchValueStreamWriter(output_stream, [self.match_sequence_d1, self.match_sequence_s1], b'', b'-')
      self.analysis_context.register_component(match_value_stream_writer, description)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      self.assertEqual(output_stream.getvalue().decode(), '25537Euro \n25538Euro \n25539Euro \n25540Euro \n')
    
    '''
    This test case sets up a set of values, which are all expected to be matched.
    The missing value string is none, so when a string does not match it is simply ignored.
    '''
    def test3atom_no_match_missing_value_string_empty(self):
      description = "Test3MatchValueStreamWriter"
      output_stream = BytesIO()
      match_context = MatchContext(b'25537Euro 25538Euro 25539Euro 25540Pfund ')
      decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
        DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      
      fixed_dme = FixedDataModelElement('s1', self.euro)
      sequence_model_element = SequenceModelElement('sequence', [decimal_integer_value_me, fixed_dme])
      match_value_stream_writer = MatchValueStreamWriter(output_stream, [self.match_sequence_d1, self.match_sequence_s1], b';', b'')
      self.analysis_context.register_component(match_value_stream_writer, description)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      match_element = decimal_integer_value_me.get_match_element('match', match_context)
      match_element.path = self.match_sequence_d1
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      self.assertEqual(output_stream.getvalue().decode(), '25537;Euro \n25538;Euro \n25539;Euro \n25540;\n')
    
    '''
    This test case sets up a set of values, which are all expected to be matched.
    The missing value string is set to a value, so when a string does not match this value is used instead.
    '''
    def test4atom_no_match_missing_value_string_set(self):
      description = "Test4MatchValueStreamWriter"
      output_stream = BytesIO()
      match_context = MatchContext(b'25537Euro 25538Euro 25539Euro 25540Pfund ')
      decimal_integer_value_me = DecimalIntegerValueModelElement('d1',
        DecimalIntegerValueModelElement.SIGN_TYPE_NONE, DecimalIntegerValueModelElement.PAD_TYPE_NONE)
      
      fixed_dme = FixedDataModelElement('s1', self.euro)
      sequence_model_element = SequenceModelElement('sequence', [decimal_integer_value_me, fixed_dme])
      match_value_stream_writer = MatchValueStreamWriter(output_stream, [self.match_sequence_d1, self.match_sequence_s1], b';', b'-')
      self.analysis_context.register_component(match_value_stream_writer, description)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      match_element = sequence_model_element.get_match_element('match', match_context)
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      match_element = decimal_integer_value_me.get_match_element('match', match_context)
      match_element.path = self.match_sequence_d1
      log_atom = LogAtom(match_context.match_data, ParserMatch(match_element), 1, match_value_stream_writer)
      match_value_stream_writer.receive_atom(log_atom)
      
      self.assertEqual(output_stream.getvalue().decode(), '25537;Euro \n25538;Euro \n25539;Euro \n25540;-\n')


if __name__ == "__main__":
    unittest.main()
