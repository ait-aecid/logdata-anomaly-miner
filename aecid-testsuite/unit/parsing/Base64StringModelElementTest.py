import unittest
from aminer.parsing.Base64StringModelElement import Base64StringModelElement
from unit.TestBase import TestBase, DummyMatchContext


class Base64StringModelElementTest(TestBase):
    """Unittests for the Base64StringModelElement."""

    base64_string_model_element = Base64StringModelElement('base64')
    match_base64 = 'match/base64'

    def test1get_id(self):
        """Test if get_id works properly."""
        base64_dme = Base64StringModelElement("s0")
        self.assertEqual(base64_dme.get_id(), "s0")

    def test2get_child_elements(self):
        """Test if get_child_elements returns None."""
        base64_dme = Base64StringModelElement("s0")
        self.assertEqual(base64_dme.get_child_elements(), None)

    def test3get_match_element_valid_match_string_with_padding(self):
        """Parse matching substring with padding from MatchContext and check if the MatchContext was updated accordingly."""
        string = b'This is some string to be encoded.'
        base64_string = b'VGhpcyBpcyBzb21lIHN0cmluZyB0byBiZSBlbmNvZGVkLg=='
        dummy_match_context = DummyMatchContext(base64_string)
        base64_dme = Base64StringModelElement("s0")
        match_element = base64_dme.get_match_element("base64", dummy_match_context)
        self.assertEqual(match_element.path, "base64/s0")
        self.assertEqual(match_element.match_string, base64_string)
        self.assertEqual(match_element.match_object, string)
        self.assertIsNone(match_element.children, None)
        self.assertEqual(dummy_match_context.match_data, base64_string)

    def test4get_match_element_valid_match_string_with_one_byte_padding(self):
        """Parse matching substring with padding from MatchContext and check if the MatchContext was updated accordingly."""
        string = b'This is some encoded strin'
        base64_string = b'VGhpcyBpcyBzb21lIGVuY29kZWQgc3RyaW4='
        dummy_match_context = DummyMatchContext(base64_string)
        base64_dme = Base64StringModelElement("s0")
        match_element = base64_dme.get_match_element("base64", dummy_match_context)
        self.assertEqual(match_element.path, "base64/s0")
        self.assertEqual(match_element.match_string, base64_string)
        self.assertEqual(match_element.match_object, string)
        self.assertIsNone(match_element.children, None)
        self.assertEqual(dummy_match_context.match_data, base64_string)

    def test5get_match_element_valid_match_string_without_padding(self):
        """Parse matching substring without padding from MatchContext and check if the MatchContext was updated accordingly."""
        string = b'This is some string to be encoded without the padding character =.'
        base64_string = b'VGhpcyBpcyBzb21lIHN0cmluZyB0byBiZSBlbmNvZGVkIHdpdGhvdXQgdGhlIHBhZGRpbmcgY2hhcmFjdGVyID0u'
        dummy_match_context = DummyMatchContext(base64_string)
        base64_dme = Base64StringModelElement("s0")
        match_element = base64_dme.get_match_element("base64", dummy_match_context)
        self.assertEqual(match_element.path, "base64/s0")
        self.assertEqual(match_element.match_string, base64_string)
        self.assertEqual(match_element.match_object, string)
        self.assertIsNone(match_element.children, None)
        self.assertEqual(dummy_match_context.match_data, base64_string)

    def test6get_match_element_valid_match_string_without_exact_length(self):
        """Parse matching substring without exact length (divisible by 4) and check if the MatchContext was updated accordingly."""
        string = b'This is some encoded strin'
        base64_string = b'VGhpcyBpcyBzb21lIGVuY29kZWQgc3RyaW4'
        dummy_match_context = DummyMatchContext(base64_string)
        base64_dme = Base64StringModelElement("s0")
        match_element = base64_dme.get_match_element("base64", dummy_match_context)
        self.assertEqual(match_element.path, "base64/s0")
        self.assertEqual(match_element.match_string, base64_string[:-(len(base64_string) % 4)])
        self.assertEqual(match_element.match_object, string[:-2])
        self.assertIsNone(match_element.children, None)
        self.assertEqual(dummy_match_context.match_data, base64_string[:-(len(base64_string) % 4)])

    def test7get_match_element_valid_match_string_with_partial_length(self):
        """Parse matching substring out of the MatchContext and check if the MatchContext was updated accordingly."""
        string = b'This is some encoded strin'
        base64_string = b'VGhpcyBpcyBzb21lIGVuY29kZWQgc3RyaW4='
        data = base64_string + b'\nContent: Public Key'
        dummy_match_context = DummyMatchContext(data)
        base64_dme = Base64StringModelElement("s0")
        match_element = base64_dme.get_match_element("base64", dummy_match_context)
        self.assertEqual(match_element.path, "base64/s0")
        self.assertEqual(match_element.match_string, base64_string)
        self.assertEqual(match_element.match_object, string)
        self.assertIsNone(match_element.children, None)
        self.assertEqual(dummy_match_context.match_data, base64_string)

    def test8get_match_element_no_match(self):
        """Parse not matching substring from MatchContext and check if the MatchContext was not changed."""
        data = b"!Hello World"
        dummy_match_context = DummyMatchContext(data)
        base64_dme = Base64StringModelElement("s0")
        match_element = base64_dme.get_match_element("base64", dummy_match_context)
        self.assertIsNone(match_element, None)
        self.assertEqual(dummy_match_context.match_data, data)

    def test9get_match_element_unicode_exception(self):
        """Parse a Base64 string which can not be decoded as UTF-8."""
        # ² encoded with ISO-8859-1
        base64_string = b'sg=='
        dummy_match_context = DummyMatchContext(base64_string)
        base64_dme = Base64StringModelElement("s0")
        match_element = base64_dme.get_match_element("base64", dummy_match_context)
        self.assertEqual(match_element.path, "base64/s0")
        self.assertEqual(match_element.match_string, base64_string)
        self.assertEqual(match_element.match_object, base64_string)
        self.assertIsNone(match_element.children, None)
        self.assertEqual(dummy_match_context.match_data, base64_string)

    def test9path_id_input_validation(self):
        """Check if element_id is validated."""
        # empty element_id
        path_id = ""
        self.assertRaises(ValueError, Base64StringModelElement, path_id)

        # bytes element_id is not allowed
        path_id = b"path"
        self.assertRaises(ValueError, Base64StringModelElement, path_id)

        # integer element_id is not allowed
        path_id = 123
        self.assertRaises(ValueError, Base64StringModelElement, path_id)

        # float element_id is not allowed
        path_id = 123.22
        self.assertRaises(ValueError, Base64StringModelElement, path_id)

        # dict element_id is not allowed
        path_id = {"id": "path"}
        self.assertRaises(ValueError, Base64StringModelElement, path_id)

        # list element_id is not allowed
        path_id = ["path"]
        self.assertRaises(ValueError, Base64StringModelElement, path_id)

    def test10performance(self):  # skipcq: PYL-R0201
        """Test the performance of the implementation. Comment this test out in normal cases."""
        import_setup = """
import copy
from unit.TestBase import DummyMatchContext
from aminer.parsing.Base64StringModelElement import Base64StringModelElement
times = 100000
"""
        string100_setup = """
# b'ASCII stands for American Standard Code for Information Interchange. Computers can only understand.'
base64_string = b'QVNDSUkgc3RhbmRzIGZvciBBbWVyaWNhbiBTdGFuZGFyZCBDb2RlIGZvciBJbmZvcm1hdGlvbiBJbnRlcmNoYW5nZS4gQ29tcHV0ZXJzIGNhb' \
                b'iBvbmx5IHVuZGVyc3RhbmQu'
"""
        string4096_setup = """
# b"ASCII stands for American Standard Code for Information Interchange. Computers can only understand numbers, so an ASCII code " \
# b"is the numerical representation of a character such as 'a' or '@' or an action of some sort. ASCII was developed a long time " \
# b"ago and now the non-printing characters are rarely used for their original purpose. Below is the ASCII character table and " \
# b"this includes descriptions of the first 32 non-printing characters. ASCII was actually designed for use with teletypes and " \
# b"so the descriptions are somewhat obscure. If someone says they want your CV however in ASCII format, all this means is they " \
# b"want 'plain' text with no formatting such as tabs, bold or underscoring - the raw format that any computer can understand. " \
# b"This is usually so they can easily import the file into their own applications without issues. Notepad.exe creates ASCII " \
# b"text, or in MS Word you can save a file as 'text only'ASCII stands for American Standard Code for Information Interchange. " \
# b"Computers can only understand numbers, so an ASCII code is the numerical representation of a character such as 'a' or '@' " \
# b"or an action of some sort. ASCII was developed a long time ago and now the non-printing characters are rarely used for their " \
# b"original purpose. Below is the ASCII character table and this includes descriptions of the first 32 non-printing characters. " \
# b"ASCII was actually designed for use with teletypes and so the descriptions are somewhat obscure. If someone says they want " \
# b"your CV however in ASCII format, all this means is they want 'plain' text with no formatting such as tabs, bold or " \
# b"underscoring - the raw format that any computer can understand. This is usually so they can easily import the file into " \
# b"their own applications without issues. Notepad.exe creates ASCII text, or in MS Word you can save a file as 'text only'" \
# b"ASCII stands for American Standard Code for Information Interchange. Computers can only understand numbers, so an ASCII " \
# b"code is the numerical representation of a character such as 'a' or '@' or an action of some sort. ASCII was developed a " \
# b"long time ago and now the non-printing characters are rarely used for their original purpose. Below is the ASCII " \
# b"character table and this includes descriptions of the first 32 non-printing characters. ASCII was actually designed for " \
# b"use with teletypes and so the descriptions are somewhat obscure. If someone says they want your CV however in ASCII format, " \
# b"all this means is they want 'plain' text with no formatting such as tabs, bold or underscoring - the raw format that any " \
# b"computer can understand. This is usually so they can easily import the file into their own applications without issues. " \
# b"Notepad.exe creates ASCII text, or in MS Word you can save a file as 'text only'ASCII stands for American Standard Code for " \
# b"Information Interchange. Computers can only understand numbers, so an ASCII code is the numerical representation of a " \
# b"character such as 'a' or '@' or an action of some sort. ASCII was developed a long time ago and now the non-printing " \
# b"characters are rarely used for their original purpose. Below is the ASCII character table and this includes descriptions " \
# b"of the first 32 non-printing characters. ASCII was actually designed for use with teletypes and so the descriptions are " \
# b"somewhat obscure. If someone says they want your CV however in ASCII format, all this means is they want 'plain' text with " \
# b"no formatting such as tabs, bold or underscoring - the raw format that any computer can understand. This is usually so they " \
# b"can easily import the file into their own applications without issues. Notepad.exe creates ASCII text, or in MS Word you " \
# b"can save a file as 'text only'ASCII stands for American Standard Code for Information Interchange. Computers can only " \
# b"understand numbers, so an ASCII code is the numerical representation of a character such as 'a' or '@' or an action of " \
# b"some sort. ASCII was developed a long time ago and now the non-printing characters are rarely used for their original " \
# b"purpose. Below is the ASCII character table and this includes descriptions of the first 32 non-prin"
base64_string = b"QVNDSUkgc3RhbmRzIGZvciBBbWVyaWNhbiBTdGFuZGFyZCBDb2RlIGZvciBJbmZvcm1hdGlvbiBJbnRlcmNoYW5nZS4gQ29tcHV0ZXJzIGNhbiBvbmx5IHV" \
                b"uZGVyc3RhbmQgbnVtYmVycywgc28gYW4gQVNDSUkgY29kZSBpcyB0aGUgbnVtZXJpY2FsIHJlcHJlc2VudGF0aW9uIG9mIGEgY2hhcmFjdGVyIHN1Y2ggYX" \
                b"MgJ2EnIG9yICdAJyBvciBhbiBhY3Rpb24gb2Ygc29tZSBzb3J0LiBBU0NJSSB3YXMgZGV2ZWxvcGVkIGEgbG9uZyB0aW1lIGFnbyBhbmQgbm93IHRoZSBub" \
                b"24tcHJpbnRpbmcgY2hhcmFjdGVycyBhcmUgcmFyZWx5IHVzZWQgZm9yIHRoZWlyIG9yaWdpbmFsIHB1cnBvc2UuIEJlbG93IGlzIHRoZSBBU0NJSSBjaGFy" \
                b"YWN0ZXIgdGFibGUgYW5kIHRoaXMgaW5jbHVkZXMgZGVzY3JpcHRpb25zIG9mIHRoZSBmaXJzdCAzMiBub24tcHJpbnRpbmcgY2hhcmFjdGVycy4gQVNDSUk" \
                b"gd2FzIGFjdHVhbGx5IGRlc2lnbmVkIGZvciB1c2Ugd2l0aCB0ZWxldHlwZXMgYW5kIHNvIHRoZSBkZXNjcmlwdGlvbnMgYXJlIHNvbWV3aGF0IG9ic2N1cm" \
                b"UuIElmIHNvbWVvbmUgc2F5cyB0aGV5IHdhbnQgeW91ciBDViBob3dldmVyIGluIEFTQ0lJIGZvcm1hdCwgYWxsIHRoaXMgbWVhbnMgaXMgdGhleSB3YW50I" \
                b"CdwbGFpbicgdGV4dCB3aXRoIG5vIGZvcm1hdHRpbmcgc3VjaCBhcyB0YWJzLCBib2xkIG9yIHVuZGVyc2NvcmluZyAtIHRoZSByYXcgZm9ybWF0IHRoYXQg" \
                b"YW55IGNvbXB1dGVyIGNhbiB1bmRlcnN0YW5kLiBUaGlzIGlzIHVzdWFsbHkgc28gdGhleSBjYW4gZWFzaWx5IGltcG9ydCB0aGUgZmlsZSBpbnRvIHRoZWl" \
                b"yIG93biBhcHBsaWNhdGlvbnMgd2l0aG91dCBpc3N1ZXMuIE5vdGVwYWQuZXhlIGNyZWF0ZXMgQVNDSUkgdGV4dCwgb3IgaW4gTVMgV29yZCB5b3UgY2FuIH" \
                b"NhdmUgYSBmaWxlIGFzICd0ZXh0IG9ubHknQVNDSUkgc3RhbmRzIGZvciBBbWVyaWNhbiBTdGFuZGFyZCBDb2RlIGZvciBJbmZvcm1hdGlvbiBJbnRlcmNoY" \
                b"W5nZS4gQ29tcHV0ZXJzIGNhbiBvbmx5IHVuZGVyc3RhbmQgbnVtYmVycywgc28gYW4gQVNDSUkgY29kZSBpcyB0aGUgbnVtZXJpY2FsIHJlcHJlc2VudGF0" \
                b"aW9uIG9mIGEgY2hhcmFjdGVyIHN1Y2ggYXMgJ2EnIG9yICdAJyBvciBhbiBhY3Rpb24gb2Ygc29tZSBzb3J0LiBBU0NJSSB3YXMgZGV2ZWxvcGVkIGEgbG9" \
                b"uZyB0aW1lIGFnbyBhbmQgbm93IHRoZSBub24tcHJpbnRpbmcgY2hhcmFjdGVycyBhcmUgcmFyZWx5IHVzZWQgZm9yIHRoZWlyIG9yaWdpbmFsIHB1cnBvc2" \
                b"UuIEJlbG93IGlzIHRoZSBBU0NJSSBjaGFyYWN0ZXIgdGFibGUgYW5kIHRoaXMgaW5jbHVkZXMgZGVzY3JpcHRpb25zIG9mIHRoZSBmaXJzdCAzMiBub24tc" \
                b"HJpbnRpbmcgY2hhcmFjdGVycy4gQVNDSUkgd2FzIGFjdHVhbGx5IGRlc2lnbmVkIGZvciB1c2Ugd2l0aCB0ZWxldHlwZXMgYW5kIHNvIHRoZSBkZXNjcmlw" \
                b"dGlvbnMgYXJlIHNvbWV3aGF0IG9ic2N1cmUuIElmIHNvbWVvbmUgc2F5cyB0aGV5IHdhbnQgeW91ciBDViBob3dldmVyIGluIEFTQ0lJIGZvcm1hdCwgYWx" \
                b"sIHRoaXMgbWVhbnMgaXMgdGhleSB3YW50ICdwbGFpbicgdGV4dCB3aXRoIG5vIGZvcm1hdHRpbmcgc3VjaCBhcyB0YWJzLCBib2xkIG9yIHVuZGVyc2Nvcm" \
                b"luZyAtIHRoZSByYXcgZm9ybWF0IHRoYXQgYW55IGNvbXB1dGVyIGNhbiB1bmRlcnN0YW5kLiBUaGlzIGlzIHVzdWFsbHkgc28gdGhleSBjYW4gZWFzaWx5I" \
                b"GltcG9ydCB0aGUgZmlsZSBpbnRvIHRoZWlyIG93biBhcHBsaWNhdGlvbnMgd2l0aG91dCBpc3N1ZXMuIE5vdGVwYWQuZXhlIGNyZWF0ZXMgQVNDSUkgdGV4" \
                b"dCwgb3IgaW4gTVMgV29yZCB5b3UgY2FuIHNhdmUgYSBmaWxlIGFzICd0ZXh0IG9ubHknQVNDSUkgc3RhbmRzIGZvciBBbWVyaWNhbiBTdGFuZGFyZCBDb2R" \
                b"lIGZvciBJbmZvcm1hdGlvbiBJbnRlcmNoYW5nZS4gQ29tcHV0ZXJzIGNhbiBvbmx5IHVuZGVyc3RhbmQgbnVtYmVycywgc28gYW4gQVNDSUkgY29kZSBpcy" \
                b"B0aGUgbnVtZXJpY2FsIHJlcHJlc2VudGF0aW9uIG9mIGEgY2hhcmFjdGVyIHN1Y2ggYXMgJ2EnIG9yICdAJyBvciBhbiBhY3Rpb24gb2Ygc29tZSBzb3J0L" \
                b"iBBU0NJSSB3YXMgZGV2ZWxvcGVkIGEgbG9uZyB0aW1lIGFnbyBhbmQgbm93IHRoZSBub24tcHJpbnRpbmcgY2hhcmFjdGVycyBhcmUgcmFyZWx5IHVzZWQg" \
                b"Zm9yIHRoZWlyIG9yaWdpbmFsIHB1cnBvc2UuIEJlbG93IGlzIHRoZSBBU0NJSSBjaGFyYWN0ZXIgdGFibGUgYW5kIHRoaXMgaW5jbHVkZXMgZGVzY3JpcHR" \
                b"pb25zIG9mIHRoZSBmaXJzdCAzMiBub24tcHJpbnRpbmcgY2hhcmFjdGVycy4gQVNDSUkgd2FzIGFjdHVhbGx5IGRlc2lnbmVkIGZvciB1c2Ugd2l0aCB0ZW" \
                b"xldHlwZXMgYW5kIHNvIHRoZSBkZXNjcmlwdGlvbnMgYXJlIHNvbWV3aGF0IG9ic2N1cmUuIElmIHNvbWVvbmUgc2F5cyB0aGV5IHdhbnQgeW91ciBDViBob" \
                b"3dldmVyIGluIEFTQ0lJIGZvcm1hdCwgYWxsIHRoaXMgbWVhbnMgaXMgdGhleSB3YW50ICdwbGFpbicgdGV4dCB3aXRoIG5vIGZvcm1hdHRpbmcgc3VjaCBh" \
                b"cyB0YWJzLCBib2xkIG9yIHVuZGVyc2NvcmluZyAtIHRoZSByYXcgZm9ybWF0IHRoYXQgYW55IGNvbXB1dGVyIGNhbiB1bmRlcnN0YW5kLiBUaGlzIGlzIHV" \
                b"zdWFsbHkgc28gdGhleSBjYW4gZWFzaWx5IGltcG9ydCB0aGUgZmlsZSBpbnRvIHRoZWlyIG93biBhcHBsaWNhdGlvbnMgd2l0aG91dCBpc3N1ZXMuIE5vdG" \
                b"VwYWQuZXhlIGNyZWF0ZXMgQVNDSUkgdGV4dCwgb3IgaW4gTVMgV29yZCB5b3UgY2FuIHNhdmUgYSBmaWxlIGFzICd0ZXh0IG9ubHknQVNDSUkgc3RhbmRzI" \
                b"GZvciBBbWVyaWNhbiBTdGFuZGFyZCBDb2RlIGZvciBJbmZvcm1hdGlvbiBJbnRlcmNoYW5nZS4gQ29tcHV0ZXJzIGNhbiBvbmx5IHVuZGVyc3RhbmQgbnVt" \
                b"YmVycywgc28gYW4gQVNDSUkgY29kZSBpcyB0aGUgbnVtZXJpY2FsIHJlcHJlc2VudGF0aW9uIG9mIGEgY2hhcmFjdGVyIHN1Y2ggYXMgJ2EnIG9yICdAJyB" \
                b"vciBhbiBhY3Rpb24gb2Ygc29tZSBzb3J0LiBBU0NJSSB3YXMgZGV2ZWxvcGVkIGEgbG9uZyB0aW1lIGFnbyBhbmQgbm93IHRoZSBub24tcHJpbnRpbmcgY2" \
                b"hhcmFjdGVycyBhcmUgcmFyZWx5IHVzZWQgZm9yIHRoZWlyIG9yaWdpbmFsIHB1cnBvc2UuIEJlbG93IGlzIHRoZSBBU0NJSSBjaGFyYWN0ZXIgdGFibGUgY" \
                b"W5kIHRoaXMgaW5jbHVkZXMgZGVzY3JpcHRpb25zIG9mIHRoZSBmaXJzdCAzMiBub24tcHJpbnRpbmcgY2hhcmFjdGVycy4gQVNDSUkgd2FzIGFjdHVhbGx5" \
                b"IGRlc2lnbmVkIGZvciB1c2Ugd2l0aCB0ZWxldHlwZXMgYW5kIHNvIHRoZSBkZXNjcmlwdGlvbnMgYXJlIHNvbWV3aGF0IG9ic2N1cmUuIElmIHNvbWVvbmU" \
                b"gc2F5cyB0aGV5IHdhbnQgeW91ciBDViBob3dldmVyIGluIEFTQ0lJIGZvcm1hdCwgYWxsIHRoaXMgbWVhbnMgaXMgdGhleSB3YW50ICdwbGFpbicgdGV4dC" \
                b"B3aXRoIG5vIGZvcm1hdHRpbmcgc3VjaCBhcyB0YWJzLCBib2xkIG9yIHVuZGVyc2NvcmluZyAtIHRoZSByYXcgZm9ybWF0IHRoYXQgYW55IGNvbXB1dGVyI" \
                b"GNhbiB1bmRlcnN0YW5kLiBUaGlzIGlzIHVzdWFsbHkgc28gdGhleSBjYW4gZWFzaWx5IGltcG9ydCB0aGUgZmlsZSBpbnRvIHRoZWlyIG93biBhcHBsaWNh" \
                b"dGlvbnMgd2l0aG91dCBpc3N1ZXMuIE5vdGVwYWQuZXhlIGNyZWF0ZXMgQVNDSUkgdGV4dCwgb3IgaW4gTVMgV29yZCB5b3UgY2FuIHNhdmUgYSBmaWxlIGF" \
                b"zICd0ZXh0IG9ubHknQVNDSUkgc3RhbmRzIGZvciBBbWVyaWNhbiBTdGFuZGFyZCBDb2RlIGZvciBJbmZvcm1hdGlvbiBJbnRlcmNoYW5nZS4gQ29tcHV0ZX" \
                b"JzIGNhbiBvbmx5IHVuZGVyc3RhbmQgbnVtYmVycywgc28gYW4gQVNDSUkgY29kZSBpcyB0aGUgbnVtZXJpY2FsIHJlcHJlc2VudGF0aW9uIG9mIGEgY2hhc" \
                b"mFjdGVyIHN1Y2ggYXMgJ2EnIG9yICdAJyBvciBhbiBhY3Rpb24gb2Ygc29tZSBzb3J0LiBBU0NJSSB3YXMgZGV2ZWxvcGVkIGEgbG9uZyB0aW1lIGFnbyBh" \
                b"bmQgbm93IHRoZSBub24tcHJpbnRpbmcgY2hhcmFjdGVycyBhcmUgcmFyZWx5IHVzZWQgZm9yIHRoZWlyIG9yaWdpbmFsIHB1cnBvc2UuIEJlbG93IGlzIHR" \
                b"oZSBBU0NJSSBjaGFyYWN0ZXIgdGFibGUgYW5kIHRoaXMgaW5jbHVkZXMgZGVzY3JpcHRpb25zIG9mIHRoZSBmaXJzdCAzMiBub24tcHJpbg=="
"""
        end_setup = """
dummy_match_context = DummyMatchContext(base64_string)
dummy_match_context_list = [copy.deepcopy(dummy_match_context) for _ in range(times)]
base64_dme = Base64StringModelElement("s0")

def run():
    match_context = dummy_match_context_list.pop(0)
    base64_dme.get_match_element("base64", match_context)
"""
        _setup100 = import_setup + string100_setup + end_setup
        _setup4096 = import_setup + string4096_setup + end_setup
        # import timeit
        # times = 100000
        # print("All text lengths are given from the original text. Base64 encoding needs 33% more characters."
        #       " Every text length is run 100.000 times.")
        # t = timeit.timeit(setup=_setup100, stmt="run()", number=times)
        # print("Text length 100: ", t)
        # t = timeit.timeit(setup=_setup4096, stmt="run()", number=times)
        # print("Text length 4096: ", t)


if __name__ == "__main__":
    unittest.main()
