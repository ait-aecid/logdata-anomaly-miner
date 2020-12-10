"""This module defines a parser for tomcat."""

from aminer.parsing import AnyByteDataModelElement
from aminer.parsing import DecimalIntegerValueModelElement
from aminer.parsing import FirstMatchModelElement
from aminer.parsing import FixedDataModelElement
from aminer.parsing import SequenceModelElement


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
