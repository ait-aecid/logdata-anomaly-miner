"""This module defines a generated parser model."""

from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DateTimeModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import FixedWordlistDataModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import SequenceModelElement

def get_model():

    """This model defines how to parse Apache Error logs from the AIT-LDS."""

    model = SequenceModelElement('model', [
        FixedDataModelElement('sp1', b'['),
        FixedWordlistDataModelElement('day', [b'Mon', b'Tue', b'Wed', b'Thu', b'Fri', b'Sat', b'Sun']),
        FixedDataModelElement('sp2', b' '),
        DateTimeModelElement('time', b'%b %d %H:%M:%S.%f %Y'),
        FixedDataModelElement('error_str', b'] [:error] [pid '),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('sp3', b'] [client '),
        IpAddressDataModelElement('client_ip'),
        FixedDataModelElement('colon', b':'),
        DecimalIntegerValueModelElement('client_port'),
        FixedDataModelElement('php', b'] PHP '),
        FirstMatchModelElement('fphp', [
            SequenceModelElement('warning', [
                FixedDataModelElement('warning_str', b'Warning:  '),
                FirstMatchModelElement('warning', [
                    SequenceModelElement('declaration', [
                        FixedDataModelElement('declaration_str', b'Declaration of '),
                        DelimitedDataModelElement('function', b')'),
                        FixedDataModelElement('compatible_str', b') should be compatible with '),
                        DelimitedDataModelElement('function2', b')'),
                        FixedDataModelElement('compatible_str', b') in '),
                        DelimitedDataModelElement('path', b' '),
                        FixedDataModelElement('compatible_str', b' on line '),
                        DecimalIntegerValueModelElement('line'),
                        FixedDataModelElement('referer_str', b', referer: '),
                        AnyByteDataModelElement('referer')]),
                    SequenceModelElement('system', [
                        FixedDataModelElement('system_str', b'system(): Cannot execute a blank command in '),
                        DelimitedDataModelElement('path', b' '),
                        FixedDataModelElement('compatible_str', b' on line '),
                        DecimalIntegerValueModelElement('line')])])]),
            SequenceModelElement('notice', [
                FixedDataModelElement('notice_str', b'Notice:  Undefined index: '),
                DelimitedDataModelElement('command', b' '),
                FixedDataModelElement('sp', b' in '),
                DelimitedDataModelElement('path', b' '),
                FixedDataModelElement('compatible_str', b' on line '),
                DecimalIntegerValueModelElement('line')]),
            SequenceModelElement('deprecated', [
                FixedDataModelElement('deprecated_str', b'Deprecated:  Methods with the same name as their class '
                                      b'will not be constructors in a future version of PHP; '),
                DelimitedDataModelElement('class', b' '),
                FixedDataModelElement('constructor_str', b' has a deprecated constructor in '),
                DelimitedDataModelElement('path', b' '),
                FixedDataModelElement('compatible_str', b' on line '),
                DecimalIntegerValueModelElement('line'),
                FixedDataModelElement('referer_str', b', referer: '),
                AnyByteDataModelElement('referer'),
                ])])])

    return model
