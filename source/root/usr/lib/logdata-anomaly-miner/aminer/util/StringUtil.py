import logging
from aminer import AMinerConfig


def decode_string_as_byte_string(string):
    """
    Decode a string produced by the encode function encodeByteStringAsString(byteString) below.
    @return string.
    """
    decoded = b''
    count = 0
    while count < len(string):
        if string[count] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!"#$&\'()*+,-./:;<=>?@[]\\^_`{}|~ ':
            decoded += bytes(string[count], 'ascii')
            count += 1
        elif string[count] == '%':
            decoded += bytearray((int(string[count + 1:count + 3], 16),))
            count += 3
        else:
            msg = 'Invalid encoded character'
            logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)
    return decoded


def encode_byte_string_as_string(byte_string):
    r"""
    Encode an arbitrary byte string to a string.
    This is achieved by replacing all non ascii-7 bytes and all non printable ascii-7 bytes and % character by replacing with their escape
    sequence %[hex]. For example byte string b'/\xc3' is encoded to '/%c3'
    @return a string with decoded name.
    """
    encoded = ''
    for byte in byte_string:
        if byte in b'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!"#$&\'()*+,-./:;<=>?@[]\\^_`{}|~ ':
            encoded += chr(byte)
        else:
            encoded += '%%%02x' % byte
    return encoded
