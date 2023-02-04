"""
Some useful string-functions.

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
import logging
import sys
import os
from aminer.AminerConfig import DEBUG_LOG_NAME


colflame = ("\033[31m"
            "           *     (       )       (     \n"
            "   (     (  `    )\\ ) ( /(       )\\ )  \n"
            "   )\\    )\\))(  (()/( )\\()) (   (()/(  \n"
            "\033[33m"
            "((((_)( ((_)()\\  /(_))(_)\\  )\\   /(_)) \n"
            " )\\ _ )\\(_()((_)(_))  _((_)((_) (_))   \n"
            " (_)\033[39m_\\\033[33m()\033[39m|  \\/  ||_ _|| \\| || __|| _ \\  \n"
            "  / _ \\ | |\\/| | | | | .` || _| |   /  \n"
            " /_/ \\_\\|_|  |_||___||_|\\_||___||_|_\\  "
            "\033[39m")

flame = ("           *     (       )       (     \n"
         "   (     (  `    )\\ ) ( /(       )\\ )  \n"
         "   )\\    )\\))(  (()/( )\\()) (   (()/(  \n"
         "((((_)( ((_)()\\  /(_))(_)\\  )\\   /(_)) \n"
         " )\\ _ )\\(_()((_)(_))  _((_)((_) (_))   \n"
         " (_)_\\()|  \\/  ||_ _|| \\| || __|| _ \\  \n"
         "  / _ \\ | |\\/| | | | | .` || _| |   /  \n"
         " /_/ \\_\\|_|  |_||___||_|\\_||___||_|_\\  ")


def supports_color():
    """
    Return True if the running system's terminal supports color, and False otherwise.
    The function was borrowed from the django-project (https://github.com/django/django/blob/master/django/core/management/color.py)
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    # isatty is not always implemented, #6223.
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    return supported_platform and is_a_tty


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
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
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
            encoded += '%%%02x' % byte  # skipcq: PYL-C0209
    return encoded
