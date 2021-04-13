"""This module defines a parser for tomcat."""

from aminer.parsing.AnyByteDataModelElement import AnyByteDataModelElement
from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
from aminer.parsing.FixedDataModelElement import FixedDataModelElement
from aminer.parsing.SequenceModelElement import SequenceModelElement


def get_model():
    """Return the model."""
    type_children = [
        FixedDataModelElement('start', b' * Starting Tomcat servlet engine tomcat7'),
        FixedDataModelElement('stop', b' * Stopping Tomcat servlet engine tomcat7'),
        FixedDataModelElement('done', b'   ...done.'),
        AnyByteDataModelElement('unparsed')
    ]

    model = SequenceModelElement('tomcat7', [
        FixedDataModelElement('sname', b'tomcat7['),
        DecimalIntegerValueModelElement('pid'),
        FixedDataModelElement('s0', b']: '),
        FirstMatchModelElement('msg', type_children)
    ])
    return model
