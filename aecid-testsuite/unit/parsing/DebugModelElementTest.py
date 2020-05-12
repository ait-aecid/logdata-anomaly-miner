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
      output = StringIO()
      sys.stderr = output
      debug_model_element = DebugModelElement('debug')
      self.assertEqual(output.getvalue(), 'DebugModelElement %s added\n' % debug_model_element.element_id)
      
      output.seek(0)
      output.truncate(0)
      
      matchContext = MatchContext(b'some data')
      matchElement = debug_model_element.get_match_element('debugMatch', matchContext)
      self.assertEqual(output.getvalue(), 'DebugModelElement path = "%s", unmatched = "%s"\n'
        % (matchElement.get_path(), matchContext.match_data))


if __name__ == "__main__":
    unittest.main()
