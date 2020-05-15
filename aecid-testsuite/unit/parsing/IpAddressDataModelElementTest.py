import unittest
from aminer.parsing.MatchContext import MatchContext
from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement


class IpAddressDataModelElementTest(unittest.TestCase):

    wrong_ip_address = 'wrong ip address.'
    ip_address_bytes_wrong = 'ip address bytes are wrong.'
    match_context_unexpected = 'match context is not as expected.'
    followed_by = b' followed by some text'
    match_element_unexpected = 'No MatchElement was expected.'

    '''
    This test case checks the functionality by parsing a real IP-addresses.
    The boundary values for IP-addresses is 0.0.0.0 - 255.255.255.255
    '''
    def test1real_ip_address(self):
      match_context = MatchContext(b'192.168.0.155 followed by some text')
      ip_address_data_model_element = IpAddressDataModelElement('dest')
      match_element = ip_address_data_model_element.get_match_element(None, match_context)
      self.assertEqual(match_element.get_match_string(), b'192.168.0.155', self.wrong_ip_address)
      self.assertEqual(match_element.get_match_object().to_bytes(4, byteorder='big'), b'\xc0\xa8\x00\x9b', self.ip_address_bytes_wrong)
      self.assertEqual(match_context.match_data, self.followed_by, self.match_context_unexpected)
      
      match_context = MatchContext(b'0.0.0.0 followed by some text')
      ip_address_data_model_element = IpAddressDataModelElement('dest')
      match_element = ip_address_data_model_element.get_match_element(None, match_context)
      self.assertEqual(match_element.get_match_string(), b'0.0.0.0', self.wrong_ip_address)
      self.assertEqual(match_element.get_match_object().to_bytes(4, byteorder='big'), b'\x00\x00\x00\x00', self.ip_address_bytes_wrong)
      self.assertEqual(match_context.match_data, self.followed_by, self.match_context_unexpected)
      
      match_context = MatchContext(b'255.255.255.255 followed by some text')
      ip_address_data_model_element = IpAddressDataModelElement('dest')
      match_element = ip_address_data_model_element.get_match_element(None, match_context)
      self.assertEqual(match_element.get_match_string(), b'255.255.255.255', self.wrong_ip_address)
      self.assertEqual(match_element.get_match_object().to_bytes(4, byteorder='big'), b'\xff\xff\xff\xff', self.ip_address_bytes_wrong)
      self.assertEqual(match_context.match_data, self.followed_by, self.match_context_unexpected)
    
    '''
    This test case checks if wrong formats are determined.
    Boundary values are exceeded.
    '''
    def test2wrong_ip_address(self):
      match_context = MatchContext(b'192. 168.0.155 followed by some text')
      ip_address_data_model_element = IpAddressDataModelElement('dest')
      match_element = ip_address_data_model_element.get_match_element(None, match_context)
      self.assertEqual(match_element, None, self.match_element_unexpected)
      self.assertEqual(match_context.match_data, b'192. 168.0.155 followed by some text', self.match_context_unexpected)
      
      match_context = MatchContext(b'256.168.0.155 followed by some text')
      ip_address_data_model_element = IpAddressDataModelElement('dest')
      match_element = ip_address_data_model_element.get_match_element(None, match_context)
      self.assertEqual(match_element, None, self.match_element_unexpected)
      self.assertEqual(match_context.match_data, b'256.168.0.155 followed by some text', self.match_context_unexpected)
    
    '''
    This test case checks if the ip address starts with a digit.
    Hexadecimal ip addresses are not allowed.
    '''
    def test3starts_with_digit(self):
      match_context = MatchContext(b'\xc0\xa8\x00\x9b')
      ip_address_data_model_element = IpAddressDataModelElement('dest')
      match_element = ip_address_data_model_element.get_match_element(None, match_context)
      self.assertEqual(match_element, None, self.match_element_unexpected)
      self.assertEqual(match_context.match_data, b'\xc0\xa8\x00\x9b', self.match_context_unexpected)
    
    '''
    This test case checks if valid ip addresses are found, even if it is followed by other numbers.
    '''
    def test4longer_ip_address(self):
      match_context = MatchContext(b'192.168.0.155.22 followed by some text')
      ip_address_data_model_element = IpAddressDataModelElement('dest')
      match_element = ip_address_data_model_element.get_match_element(None, match_context)
      self.assertEqual(match_element.get_match_string(), b'192.168.0.155', self.wrong_ip_address)
      self.assertEqual(match_element.get_match_object().to_bytes(4, byteorder='big'), b'\xc0\xa8\x00\x9b', self.ip_address_bytes_wrong)
      self.assertEqual(match_context.match_data, b'.22 followed by some text', self.match_context_unexpected)


if __name__ == "__main__":
    unittest.main()
