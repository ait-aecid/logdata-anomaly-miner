import unittest
from aminer.util.JsonUtil import encode_object, decode_object, dump_as_json, load_json
from unit.TestBase import TestBase


class JsonUtilTest(TestBase):
    """Unittests for the JsonUtil class."""

    def test1encode_decode(self):
        """This test method encodes/decodes objects into/from the JSON-format."""
        # strings
        s = 'this is a normal string to be serialized'
        pre = 'string:'
        enc = encode_object(s)
        self.assertEqual(enc, pre + s)
        self.assertEqual(decode_object(enc), s)

        # bytes
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

        # iterables
        lis = [b'1', '2', 3, ['4'], {'5', '6'}, {'key': 'val', tuple([1,"2",None]): 'otherVal'}]
        res = ['bytes:1', 'string:2', 3, ['string:4'], ['string:' + x for x in lis[4]], {'string:key': 'string:val', "tuple:(1, '2', None)": 'string:otherVal'}]
        enc = encode_object(lis)
        self.assertEqual(enc, res)
        lis[4] = list(lis[4])
        self.assertEqual(decode_object(enc), lis)

        tup = (b'1', '2', 3, ['4'], {'5', '6'}, {'key': 'val', tuple([1,"2",None]): 'otherVal'})
        enc = encode_object(tup)
        self.assertEqual(enc, res)
        self.assertEqual(decode_object(enc), lis)

        dictionary = {'user': 'defaultUser', 'password': b'topSecret', 'id': 25}
        enc = encode_object(dictionary)
        self.assertEqual(enc, {'string:user': 'string:defaultUser', 'string:password': 'bytes:topSecret', 'string:id': 25})
        self.assertEqual(decode_object(enc), dictionary)

        # booleans
        boolean1 = True
        enc = encode_object(boolean1)
        self.assertEqual(enc, True)
        self.assertEqual(decode_object(enc), True)

        # integers
        integer1 = 125
        enc = encode_object(integer1)
        self.assertEqual(enc, 125)
        self.assertEqual(decode_object(enc), 125)

        # floats
        float1 = 125.25
        enc = encode_object(float1)
        self.assertEqual(enc, 125.25)
        self.assertEqual(decode_object(enc), 125.25)


    def test2dump_load_json(self):
        """
        This test method serializes an object by encoding it into a JSON-formatted string.
        Annotation: external classes and methods are not tested and assumed to be working as intend.
        """
        tup = (b'1', '2', 3, ['4'])
        enc = '["bytes:1", "string:2", 3, ["string:4"]]'
        self.assertEqual(dump_as_json(tup), enc)
        self.assertEqual(load_json(enc), list(tup))

    def test3load_json(self):
        """
        This test method loads a serialized string and deserializes it by decoding into an object.
        Annotation: external classes and methods are not tested and assumed to be working as intend.
        """


if __name__ == "__main__":
    unittest.main()
