"""This module defines a generated parser model."""

from aminer.parsing import DateTimeModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import DelimitedDataModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import IpAddressDataModelElement
from aminer.parsing import SequenceModelElement

def get_model():

    """This model defines how to parse Suricata Fast logs from the AIT-LDS."""

    model = SequenceModelElement('model', [
        DateTimeModelElement('time', b'%m/%d/%Y-%H:%M:%S.%f'),
        FixedDataModelElement('brack_str1', b'  [**] ['),
        DecimalIntegerValueModelElement('id1'),
        FixedDataModelElement('sep1', b':'),
        DecimalIntegerValueModelElement('id2'),
        FixedDataModelElement('sep2', b':'),
        DecimalIntegerValueModelElement('id3'),
        FixedDataModelElement('sep3', b'] '),
        DelimitedDataModelElement('message', b' [**] '),
        FixedDataModelElement('classficiation_str', b' [**] [Classification: '),
        DelimitedDataModelElement('classification', b']'),
        FixedDataModelElement('priority_str', b'] [Priority: '),
        DecimalIntegerValueModelElement('priority'),
        FixedDataModelElement('brack_str1', b'] {'),
        DelimitedDataModelElement('conn', b'}'),
        FixedDataModelElement('brack_str2', b'} '),
        IpAddressDataModelElement('src_ip'),
        FixedDataModelElement('colon', b':'),
        DecimalIntegerValueModelElement('src_port'),
        FixedDataModelElement('arrow_str', b' -> '),
        IpAddressDataModelElement('dst_ip'),
        FixedDataModelElement('colon', b':'),
        DecimalIntegerValueModelElement('dst_port'),
        ])

    return model
