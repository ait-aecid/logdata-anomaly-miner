import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.HexStringModelElement import HexStringModelElement


class HexStringModelElementTest(unittest.TestCase):

    '''
    Try all values and check if the desired results are produced.
    '''
    def test1check_all_values(self):
      self.allowed_chars = [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9',
        b'a', b'b', b'c', b'd', b'e', b'f']
      self.char1 = b'\x00'
      self.char2 = b'\x00'
      self.hex_string_model_element = HexStringModelElement('id')
      
      while ord(self.char2) < ord(b'\x7F'):
        self.match_context = MatchContext(self.char2 + self.char1)
        self.match_element = self.hex_string_model_element.get_match_element('match', self.match_context)
        if self.char2 in self.allowed_chars and self.char1 in self.allowed_chars:
          self.assertEqual(self.match_element.get_match_object(), self.char2 + self.char1)
        else:
          self.assertEqual(self.match_element, None)
        if ord(self.char1) == 0x7f:
          self.char1 = b'\x00'
          self.char2 = bytes(chr(ord(self.char2)+1), 'utf-8')
        else:
          self.char1 = bytes(chr(ord(self.char1)+1), 'utf-8')
        
      
      self.allowed_chars = self.allowed_chars = [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9',
        b'A', b'B', b'C', b'D', b'E', b'F']
      self.char1 = b'\x00'
      self.char2 = b'\x00'
      self.hex_string_model_element = HexStringModelElement('id', True)
      
      while ord(self.char2) < ord(b'\x7F'):
        self.match_context = MatchContext(self.char2 + self.char1)
        self.match_element = self.hex_string_model_element.get_match_element('match', self.match_context)
        if self.char2 in self.allowed_chars and self.char1 in self.allowed_chars:
          self.assertEqual(self.match_element.get_match_object(), self.char2 + self.char1)
        else:
          self.assertEqual(self.match_element, None)
        if ord(self.char1) == 0x7f:
          self.char1 = b'\x00'
          self.char2 = bytes(chr(ord(self.char2)+1), 'utf-8')
        else:
          self.char1 = bytes(chr(ord(self.char1)+1), 'utf-8')


if __name__ == "__main__":
    unittest.main()