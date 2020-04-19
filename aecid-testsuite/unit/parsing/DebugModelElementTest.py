import unittest
from _io import StringIO
from aminer.parsing.DebugModelElement import DebugModelElement
import sys
from aminer.parsing.MatchContext import MatchContext


class DebugModelElementTest(unittest.TestCase):

    '''
    This test case checks if the DebugModelElement was initiated and the output was correct.
    '''
    def test1start_debugging(self):
      self.output = StringIO()
      sys.stderr = self.output
      self.debug_model_element = DebugModelElement('debug')
      self.assertEqual(self.output.getvalue(), 'DebugModelElement %s added\n' % self.debug_model_element.element_id)
      
      self.output.seek(0)
      self.output.truncate(0)
      
      self.matchContext = MatchContext(b'some data')
      self.matchElement = self.debug_model_element.get_match_element('debugMatch', self.matchContext)
      self.assertEqual(self.output.getvalue(), 'DebugModelElement path = "%s", unmatched = "%s"\n'
        % (self.matchElement.get_path(), self.matchContext.match_data))


if __name__ == "__main__":
    unittest.main()