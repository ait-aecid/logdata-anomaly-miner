import unittest
from aminer.util.JsonUtil import encode_object, decode_object, dump_as_json, load_json
from unit.TestBase import TestBase


class JsonUtilTest(TestBase):

    def test1encode_decode_strings2_json(self):
        """This test method encodes/decodes string objects into/from the JSON-format."""
        s = 'this is a normal string to be serialized'
        pre = 'string:'
        enc = encode_object(s)
        self.assertEqual(enc, pre + s)
        self.assertEqual(decode_object(enc), s)

    def test2encode_decode_bytes2_json(self):
        """This test method encodes/decodes bytes objects into/from the JSON-format."""
        s = b'this is a bytestring to be serialized'
        pre = b'bytes:'
        enc = encode_object(s)
        self.assertEqual(enc, pre.decode() + s.decode())
        self.assertEqual(decode_object(s), s)
        self.assertEqual(decode_object(enc), s)

        s = bytes.fromhex('001B')
        enc = encode_object(s)
        self.assertEqual(enc, pre.decode() + '%00%1b')
        self.assertEqual(decode_object(enc), s)

    def test3encode_decode_iterables2_json(self):
        """This test method encodes/decodes list, tuple and dictionary objects into/from the JSON-format."""
        lis = [b'1', '2', 3, ['4']]
        res = ['bytes:1', 'string:2', 3, ['string:4']]
        enc = encode_object(lis)
        self.assertEqual(enc, res)
        self.assertEqual(decode_object(enc), lis)

        tup = (b'1', '2', 3, ['4'])
        enc = encode_object(tup)
        self.assertEqual(enc, res)
        self.assertEqual(decode_object(enc), lis)

        dictionary = {'user': 'defaultUser', 'password': b'topSecret', 'id': 25}
        enc = encode_object(dictionary)
        self.assertEqual(enc, {'string:user': 'string:defaultUser', 'string:password': 'bytes:topSecret', 'string:id': 25})
        self.assertEqual(decode_object(enc), dictionary)

    def test4encode_decode_booleans2_json(self):
        """This test method encodes/decodes booleans objects into/from the JSON-format."""
        boolean1 = True
        enc = encode_object(boolean1)
        self.assertEqual(enc, True)
        self.assertEqual(decode_object(enc), True)

    def test5encode_decode_decimals2_json(self):
        """This test method encodes/decodes integer and float objects into/from the JSON-format."""
        integer1 = 125
        enc = encode_object(integer1)
        self.assertEqual(enc, 125)
        self.assertEqual(decode_object(enc), 125)

    def test6dump_as_json(self):
        """This test method serializes an object by encoding it into a JSON-formatted string. Annotation: external classes and methods
        are not tested and assumed to be working as intend."""
        tup = (b'1', '2', 3, ['4'])
        self.assertEqual(dump_as_json(tup), '["bytes:1", "string:2", 3, ["string:4"]]')

    def test7load_json(self):
        """This test method loads a serialized string and deserializes it by decoding into an object. Annotation: external classes and
        methods are not tested and assumed to be working as intend."""
        obj = '["bytes:1", "string:2", 3, ["string:4"]]'
        self.assertEqual(load_json(obj), [b'1', '2', 3, ['4']])


if __name__ == "__main__":
    unittest.main()
