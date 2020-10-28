"""This module converts json strings to object structures also supporting byte array structures.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""
import json
import logging

from aminer import AMinerConfig
from aminer.util import encode_byte_string_as_string, decode_string_as_byte_string


def dump_as_json(input_object):
    """Dump an input object encoded as string"""
    return json.dumps(encode_object(input_object))


def load_json(input_string):
    """Load an string encoded as object structure"""
    return decode_object(json.loads(input_string))


def encode_object(term):
    """@param term return an object encoded as string"""
    encoded_object = ''
    if isinstance(term, str):
        encoded_object = 'string:' + term
    elif isinstance(term, bytes):
        encoded_object = 'bytes:' + encode_byte_string_as_string(term)
    elif isinstance(term, (list, tuple)):
        encoded_object = [encode_object(item) for item in term]
    elif isinstance(term, dict):
        encoded_object = {}
        for key, var in term.items():
            key = encode_object(key)
            var = encode_object(var)
            encoded_object[key] = var
    elif isinstance(term, (bool, int, float)) or term is None:
        encoded_object = term
    else:
        msg = 'Unencodeable object %s' % type(term)
        logging.getLogger(AMinerConfig.DEBUG_LOG_NAME).error(msg)
        raise Exception(msg)

    return encoded_object


def decode_object(term):
    """@param term return a string decoded as object structure"""
    decoded_object = ''
    if isinstance(term, str) and term.startswith('string:'):
        decoded_object = term[7:]
    elif isinstance(term, str) and term.startswith('bytes:'):
        decoded_object = term[6:]
        decoded_object = decode_string_as_byte_string(decoded_object)
    elif isinstance(term, list):
        decoded_object = [decode_object(item) for item in term]
    elif isinstance(term, dict):
        decoded_object = {}
        for key, var in term.items():
            key = decode_object(key)
            var = decode_object(var)
            decoded_object[key] = var
    else:
        decoded_object = term
    return decoded_object
