import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.ElementValueBranchModelElement import ElementValueBranchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement


class ElementValueBranchModelElementTest(unittest.TestCase):

  def test1(self):
    fixed_data_me1 = FixedDataModelElement("fixed 1", b'match ')
    fixed_data_me2 = FixedDataModelElement("fixed 2", b'fixed String')
    fixed_wordlist_data_model_element = FixedWordlistDataModelElement("wordlist", [b'data: ', b'string: '])
    decimal_integer_value_model_element = DecimalIntegerValueModelElement("decimal")
    seq1 = SequenceModelElement("seq1", [fixed_data_me1, fixed_wordlist_data_model_element])
    seq2 = SequenceModelElement("seq2", [fixed_data_me1, fixed_wordlist_data_model_element, fixed_data_me2])
    first_match_me = FirstMatchModelElement("first", [seq1, seq2])
    element_value_branch_model_element = ElementValueBranchModelElement("id", first_match_me, "wordlist",
      {'1':decimal_integer_value_model_element, '2':fixed_data_me2})
    match_context = MatchContext(b'match string: fixed String')
    match_element = element_value_branch_model_element.get_match_element("elementValueBranchME match", match_context)
    print(match_element)


if __name__ == "__main__":
    unittest.main()