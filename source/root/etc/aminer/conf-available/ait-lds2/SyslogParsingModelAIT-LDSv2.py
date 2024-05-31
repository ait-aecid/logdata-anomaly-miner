"""This module defines a generated parser model."""
import SyslogParsingModel


def get_model():
    """Return a model to parse Syslogs from the AIT-LDS."""

    model = SyslogParsingModel.get_model()
    model.children[0].start_year = 2022

    return model
