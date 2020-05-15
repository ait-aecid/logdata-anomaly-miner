import unittest
from aminer.parsing.MatchElement import MatchElement


class MatchElementTest(unittest.TestCase):

    '''
    This test case checks, whether a Exception is raised, when the path is None or empty and children are passed.
    '''
    def test1_child_elements_with_no_path(self):
      self.assertRaises(Exception, MatchElement, None, b'matchString', b'matchString', 
          (MatchElement('child', b'childMatchString', b'childMatchString', [])))
      
      self.assertRaises(Exception, MatchElement, '', b'matchString', b'matchString', 
          (MatchElement('child', b'childMatchString', b'childMatchString', [])))
    
    '''
    This test case checks if all possible annotations are created correctly.
    '''
    def test2annotate_match(self):
      a3 = MatchElement('a3', b'a3', b'a3', [])
      a2 = MatchElement('a2', b'a2', b'a2', [a3])
      a1 = MatchElement('a1', b'a1', b'a1', [a2])
      b3 = MatchElement('b3', b'b3', b'b3', [])
      b2 = MatchElement('b2', b'b2', b'b2', [b3])
      b1 = MatchElement('b1', b'b1', b'b1', [b2])
      
      root_element = MatchElement('root', b'root', b'root', [a1, b1])
      
      self.assertEqual(root_element.annotate_match(None), "root: b'root' a1: b'a1' a2: b'a2' a3: b'a3' b1: b'b1' b2: b'b2' b3: b'b3'")
      self.assertEqual(root_element.annotate_match(''), "root: b'root'\n  a1: b'a1'\n    a2: b'a2'\n      a3: b'a3'\n  b1: b'b1'\n    b2: b'b2'\n      b3: b'b3'")
    
    '''
    This test case checks if all child objects are serialized correctly.
    '''
    def test3serialize_object(self):
      a3 = MatchElement('a3', b'a3', b'a3', [])
      a2 = MatchElement('a2', b'a2', b'a2', [a3])
      a1 = MatchElement('a1', b'a1', b'a1', [a2])
      b3 = MatchElement('b3', b'b3', b'b3', [])
      b2 = MatchElement('b2', b'b2', b'b2', [b3])
      b1 = MatchElement('b1', b'b1', b'b1', [b2])
      
      root_element = MatchElement('root', b'root', b'root', [a1, b1])
      
      self.assertEqual(root_element.serialize_object(), {'path': 'root', 'matchobject': b'root', 'matchString': b'root', 'children': [{'path': 'a1', 'matchobject': b'a1', 'matchString': b'a1', 'children': [{'path': 'a2', 'matchobject': b'a2', 'matchString': b'a2', 'children': [{'path': 'a3', 'matchobject': b'a3', 'matchString': b'a3', 'children': []}]}]}, {'path': 'b1', 'matchobject': b'b1', 'matchString': b'b1', 'children': [{'path': 'b2', 'matchobject': b'b2', 'matchString': b'b2', 'children': [{'path': 'b3', 'matchobject': b'b3', 'matchString': b'b3', 'children': []}]}]}]})


if __name__ == "__main__":
    unittest.main()
