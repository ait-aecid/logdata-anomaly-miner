import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ElementValueBranchModelElement import ElementValueBranchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement


class ElementValueBranchModelElementTest(unittest.TestCase):
  match = b'match '
  fixed_string = b'fixed String'
  path_to_match = b'match path: /path/to/match'
  match_data = b'match data: 25000'
  match_string = b'match string: fixed String'
  string_path_to_match = b'match string: /path/to/match'

  fixed_data_me1 = FixedDataModelElement("fixed 1", match)
  fixed_data_me2 = FixedDataModelElement("fixed 2", fixed_string)
  fixed_wordlist_data_model_element = FixedWordlistDataModelElement("wordlist", [b'data: ', b'string: '])
  decimal_integer_value_model_element = DecimalIntegerValueModelElement("decimal")
  seq1 = SequenceModelElement("seq1", [fixed_data_me1, fixed_wordlist_data_model_element])
  seq2 = SequenceModelElement("seq2", [fixed_data_me1, fixed_wordlist_data_model_element, fixed_data_me2])
  first_match_me = FirstMatchModelElement("first", [seq1, seq2])
  fixed_data_me3 = FixedDataModelElement("fixed 3", path_to_match)

  '''
  In this test case different possible parameters are used to obtain a MatchElement successfully.
  '''
  def test1_match_element_found(self):
    match_context = MatchContext(self.match_data)
    element_value_branch_model_element = ElementValueBranchModelElement("id", self.first_match_me, "wordlist",
      {0:self.decimal_integer_value_model_element, 1:self.fixed_data_me2})
    match_element = element_value_branch_model_element.get_match_element("elementValueBranchME match", match_context)
    self.assertEqual(match_element.get_path(), 'elementValueBranchME match/id')
    self.assertEqual(match_element.get_match_string(), self.match_data)
    self.assertEqual(match_element.get_match_object(), self.match_data)
    self.assertEqual(match_element.get_children()[0].get_path(), 'elementValueBranchME match/id/first/seq1')
    self.assertEqual(match_element.get_children()[0].get_match_string(), b'match data: ')
    self.assertEqual(match_element.get_children()[0].get_match_object(), b'match data: ')
    self.assertEqual(match_element.get_children()[0].get_children()[0].get_path(), 'elementValueBranchME match/id/first/seq1/fixed 1')
    self.assertEqual(match_element.get_children()[0].get_children()[0].get_match_string(), self.match)
    self.assertEqual(match_element.get_children()[0].get_children()[0].get_match_object(), self.match)
    self.assertEqual(match_element.get_children()[0].get_children()[0].get_children(), None)
    self.assertEqual(match_element.get_children()[0].get_children()[1].get_path(), 'elementValueBranchME match/id/first/seq1/wordlist')
    self.assertEqual(match_element.get_children()[0].get_children()[1].get_match_string(), b'data: ')
    self.assertEqual(match_element.get_children()[0].get_children()[1].get_match_object(), 0)
    self.assertEqual(match_element.get_children()[0].get_children()[1].get_children(), None)
    self.assertEqual(match_element.get_children()[1].get_path(), 'elementValueBranchME match/id/decimal')
    self.assertEqual(match_element.get_children()[1].get_match_string(), b'25000')
    self.assertEqual(match_element.get_children()[1].get_match_object(), 25000)
    self.assertEqual(match_element.get_children()[1].get_children(), None)
    
    
    match_context = MatchContext(self.match_string)
    match_element = element_value_branch_model_element.get_match_element("elementValueBranchME match", match_context)
    self.assertEqual(match_element.get_path(), 'elementValueBranchME match/id')
    self.assertEqual(match_element.get_match_string(), self.match_string)
    self.assertEqual(match_element.get_match_object(), self.match_string)
    self.assertEqual(match_element.get_children()[0].get_path(), 'elementValueBranchME match/id/first/seq1')
    self.assertEqual(match_element.get_children()[0].get_match_string(), b'match string: ')
    self.assertEqual(match_element.get_children()[0].get_match_object(), b'match string: ')
    self.assertEqual(match_element.get_children()[0].get_children()[0].get_path(), 'elementValueBranchME match/id/first/seq1/fixed 1')
    self.assertEqual(match_element.get_children()[0].get_children()[0].get_match_string(), self.match)
    self.assertEqual(match_element.get_children()[0].get_children()[0].get_match_object(), self.match)
    self.assertEqual(match_element.get_children()[0].get_children()[0].get_children(), None)
    self.assertEqual(match_element.get_children()[0].get_children()[1].get_path(), 'elementValueBranchME match/id/first/seq1/wordlist')
    self.assertEqual(match_element.get_children()[0].get_children()[1].get_match_string(), b'string: ')
    self.assertEqual(match_element.get_children()[0].get_children()[1].get_match_object(), 1)
    self.assertEqual(match_element.get_children()[0].get_children()[1].get_children(), None)
    self.assertEqual(match_element.get_children()[1].get_path(), 'elementValueBranchME match/id/fixed 2')
    self.assertEqual(match_element.get_children()[1].get_match_string(), self.fixed_string)
    self.assertEqual(match_element.get_children()[1].get_match_object(), self.fixed_string)
    self.assertEqual(match_element.get_children()[1].get_children(), None)
  
  '''
  In this test case all possible ways of not getting a MatchElement successfully are tested.
  '''
  def test2_match_element_not_found(self):
    #no modelMatch
    element_value_branch_model_element = ElementValueBranchModelElement("id", self.first_match_me, "wordlist",
      {0:self.decimal_integer_value_model_element, 1:self.fixed_data_me2})
    match_context = MatchContext(self.path_to_match)
    self.assertEqual(element_value_branch_model_element.get_match_element('match', match_context), None)
    self.assertEqual(match_context.match_data, self.path_to_match)
    
    # no matchChildren
    element_value_branch_model_element = ElementValueBranchModelElement("id", self.fixed_data_me3, "wordlist",
      {0:self.decimal_integer_value_model_element, 1:self.fixed_data_me2})
    match_context = MatchContext(self.path_to_match)
    self.assertEqual(element_value_branch_model_element.get_match_element('match', match_context), None)
    self.assertEqual(match_context.match_data, self.path_to_match)
    
    # no branchModel
    element_value_branch_model_element = ElementValueBranchModelElement("id", self.first_match_me, "wordlist",
      {0:self.decimal_integer_value_model_element})
    match_context = MatchContext(self.string_path_to_match)
    self.assertEqual(element_value_branch_model_element.get_match_element('match', match_context), None)
    self.assertEqual(match_context.match_data, self.string_path_to_match)
    
    # no branchMatch
    element_value_branch_model_element = ElementValueBranchModelElement("id", self.first_match_me, "wordlist",
      {0:self.decimal_integer_value_model_element, 1:self.fixed_data_me2})
    match_context = MatchContext(self.string_path_to_match)
    self.assertEqual(element_value_branch_model_element.get_match_element('match', match_context), None)
    self.assertEqual(match_context.match_data, self.string_path_to_match)
  
  '''
  In this test case the functionality of the getChildElements-method is tested.
  '''
  def test3_get_child_elements(self):
    element_value_branch_model_element = ElementValueBranchModelElement("id", self.first_match_me, "wordlist",
      {0:self.decimal_integer_value_model_element, 1:self.fixed_data_me2})
    self.assertEqual(element_value_branch_model_element.get_child_elements(),
                     [self.first_match_me, self.decimal_integer_value_model_element, self.fixed_data_me2])


if __name__ == "__main__":
    unittest.main()
