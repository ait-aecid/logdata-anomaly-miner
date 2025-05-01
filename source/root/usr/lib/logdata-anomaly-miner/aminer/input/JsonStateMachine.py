# DISCLAIMER: adapted code from
# https://stackoverflow.com/questions/6886283/how-i-can-i-lazily-read-multiple-json-values-from-a-file-stream-in-python

# A streaming byte oriented JSON parser.  Feed it a single byte at a time and
# it will emit complete objects as it comes across them.  Whitespace within and
# between objects is ignored.  This means it can parse newline delimited JSON.
import math


def json_machine(emit, next_func=None):
    def _value(byte_data):
        if not byte_data:
            return None

        if byte_data in (0x09, 0x0a, 0x0d, 0x20):
            return _value  # Ignore whitespace

        # only allow json objects in our case
        if byte_data != 0x7b and next_func is _value:
            return None

        if byte_data == 0x22:  # "
            return string_machine(on_value)

        if byte_data in (0x2b, 0x2d) or (0x30 <= byte_data < 0x3a):  # -, + or 0-9
            return number_machine(byte_data, on_number)

        if byte_data == 0x7b:  #:
            return object_machine(on_value)

        if byte_data == 0x5b:  # [
            return array_machine(on_value)

        if byte_data == 0x74:  # t
            return constant_machine(TRUE, True, on_value)

        if byte_data == 0x66:  # f
            return constant_machine(FALSE, False, on_value)

        if byte_data == 0x6e:  # n
            return constant_machine(NULL, None, on_value)

        if next_func is _value:
            return None

        return next_func(byte_data)

    def on_value(value):
        emit(value)
        return next_func

    def on_number(number, byte):
        emit(number)
        return _value(byte)

    next_func = next_func or _value
    return _value


TRUE = [0x72, 0x75, 0x65]
FALSE = [0x61, 0x6c, 0x73, 0x65]
NULL = [0x75, 0x6c, 0x6c]


def constant_machine(bytes_data, value, emit):
    i = 0
    length = len(bytes_data)

    def _constant(byte_data):
        nonlocal i
        if byte_data != bytes_data[i]:
            i += 1
            return None

        i += 1
        if i < length:
            return _constant
        return emit(value)

    return _constant


def string_machine(emit):
    string = ""

    def _string(byte_data):
        nonlocal string

        if byte_data == 0x22:  # "
            return emit(string)

        if byte_data == 0x5c:  # \
            return _escaped_string

        if byte_data & 0x80:  # UTF-8 handling
            return utf8_machine(byte_data, on_char_code)

        if byte_data < 0x20 and byte_data != 0xa:  # ASCII control character - \n is allowed
            return None

        string += chr(byte_data)
        return _string

    def _escaped_string(byte_data):
        nonlocal string

        if byte_data in (0x22, 0x5c, 0x2f):  # " \ /
            string += chr(byte_data)
            return _string

        if byte_data == 0x62:  # b
            string += "\b"
            return _string

        if byte_data == 0x66:  # f
            string += "\f"
            return _string

        if byte_data == 0x6e:  # n
            string += "\n"
            return _string

        if byte_data == 0x72:  # r
            string += "\r"
            return _string

        if byte_data == 0x74:  # t
            string += "\t"
            return _string

        if byte_data == 0x75:  # u
            return hex_machine(on_char_code)

        return None

    def on_char_code(char_code):
        nonlocal string
        string += chr(char_code)
        return _string

    return _string


# Nestable state machine for UTF-8 Decoding.
def utf8_machine(byte_data, emit):
    left = 0
    num = 0

    def _utf8(byte_data):
        nonlocal num, left
        if (byte_data & 0xc0) != 0x80:
            return None

        left = left - 1

        num |= (byte_data & 0x3f) << (left * 6)
        if left:
            return _utf8
        return emit(num)

    if 0xc0 <= byte_data < 0xe0:  # 2-byte UTF-8 Character
        left = 1
        num = (byte_data & 0x1f) << 6
        return _utf8

    if 0xe0 <= byte_data < 0xf0:  # 3-byte UTF-8 Character
        left = 2
        num = (byte_data & 0xf) << 12
        return _utf8

    if 0xf0 <= byte_data < 0xf8:  # 4-byte UTF-8 Character
        left = 3
        num = (byte_data & 0x07) << 18
        return _utf8

    return None


# Nestable state machine for hex escaped characters
def hex_machine(emit):
    left = 4
    num = 0

    def _hex(byte_data):
        nonlocal num, left

        if 0x30 <= byte_data < 0x3a:
            i = byte_data - 0x30
        elif 0x61 <= byte_data <= 0x66:
            i = byte_data - 0x57
        elif 0x41 <= byte_data <= 0x46:
            i = byte_data - 0x37
        else:
            return None

        left -= 1
        num |= i << (left * 4)

        if left:
            return _hex
        return emit(num)

    return _hex


def number_machine(byte_data, emit):
    sign = 1
    number = 0
    decimal = 0
    esign = 1
    exponent = 0
    dividend = 10
    start_with_zero = False

    def _mid(byte_data):
        if start_with_zero and byte_data not in (0x2e, 0x45, 0x65, 0x7d, 0x2c, 0xa, 0x20):  # . E e } , \n Space
            return None

        if byte_data == 0x2e:  # .
            return _decimal

        return _later(byte_data)

    def _number(byte_data):
        nonlocal number
        if 0x30 <= byte_data < 0x3a:
            number = number * 10 + (byte_data - 0x30)
            return _number

        return _mid(byte_data)

    def _start(byte_data):
        nonlocal start_with_zero
        if byte_data == 0x30:
            start_with_zero = True
            return _mid

        if 0x30 < byte_data < 0x3a:
            return _number(byte_data)

        return None

    def _decimal(byte_data):
        nonlocal decimal
        nonlocal dividend
        if 0x30 <= byte_data < 0x3a:
            decimal += (byte_data - 0x30) / dividend
            dividend *= 10
            return _decimal

        return _later(byte_data)

    def _later(byte_data):
        if byte_data in (0x45, 0x65):  # E e
            return _esign

        return _done(byte_data)

    def _esign(byte_data):
        nonlocal esign
        if byte_data == 0x2b:  # +
            return _exponent

        if byte_data == 0x2d:  # -
            esign = -1
            return _exponent

        return _exponent(byte_data)

    def _exponent(byte_data):
        nonlocal exponent
        if 0x30 <= byte_data < 0x3a:
            exponent = exponent * 10 + (byte_data - 0x30)
            return _exponent

        return _done(byte_data)

    def _done(byte_data):
        value = sign * (number + decimal)
        if exponent:
            value *= math.pow(10, esign * exponent)

        return emit(value, byte_data)

    if byte_data == 0x2d:  # -
        sign = -1
        return _start

    if byte_data == 0x2b:  # +
        return _start

    return _start(byte_data)


def array_machine(emit):
    array_data = []

    def _array(byte_data):
        if byte_data == 0x5d:  # ]
            return emit(array_data)

        return json_machine(on_value, _comma)(byte_data)

    def on_value(value):
        array_data.append(value)

    def _comma(byte_data):
        if byte_data in (0x09, 0x0a, 0x0d, 0x20):
            return _comma  # Ignore whitespace

        if byte_data == 0x2c:  # ,
            return json_machine(on_value, _comma)

        if byte_data == 0x5d:  # ]
            return emit(array_data)

        return None

    return _array


def object_machine(emit):
    object_data = {}
    key = None

    def _object(byte_data):
        if byte_data == 0x7d:  #
            return emit(object_data)

        return _key(byte_data)

    def _key(byte_data):
        if byte_data in (0x09, 0x0a, 0x0d, 0x20):
            return _object  # Ignore whitespace

        if byte_data == 0x22:
            return string_machine(on_key)

        return None

    def on_key(result):
        nonlocal key
        key = result
        return _colon

    def _colon(byte_data):
        if byte_data in (0x09, 0x0a, 0x0d, 0x20):
            return _colon  # Ignore whitespace

        if byte_data == 0x3a:  # :
            return json_machine(on_value, _comma)

        return None

    def on_value(value):
        object_data[key] = value

    def _comma(byte_data):
        if byte_data in (0x09, 0x0a, 0x0d, 0x20):
            return _comma  # Ignore whitespace

        if byte_data == 0x2c:  # ,
            return _key

        if byte_data == 0x7d:  #
            return emit(object_data)

        return None

    return _object
