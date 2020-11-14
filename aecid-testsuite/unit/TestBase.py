import unittest
import os
import shutil
import logging
from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from _io import StringIO


class TestBase(unittest.TestCase):
    """This is the base class for all unittests."""

    __configFilePath = os.getcwd()+'/unit/config/config.py'

    def setUp(self):
        """Set up all needed variables and remove persisted data."""
        self.aminer_config = AMinerConfig.load_config(self.__configFilePath)
        self.analysis_context = AnalysisContext(self.aminer_config)
        self.output_stream = StringIO()
        self.stream_printer_event_handler = StreamPrinterEventHandler(self.analysis_context, self.output_stream)
        persistence_file_name = AMinerConfig.build_persistence_file_name(self.aminer_config)
        if os.path.exists(persistence_file_name):
            shutil.rmtree(persistence_file_name)
        if not os.path.exists(persistence_file_name):
            os.makedirs(persistence_file_name)
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        """Delete all persisted data after the tests."""
        self.aminer_config = AMinerConfig.load_config(self.__configFilePath)
        persistence_file_name = AMinerConfig.build_persistence_file_name(self.aminer_config)
        if os.path.exists(persistence_file_name):
            shutil.rmtree(persistence_file_name)
        if not os.path.exists(persistence_file_name):
            os.makedirs(persistence_file_name)
        logging.disable(logging.NOTSET)

    def reset_output_stream(self):
        """Reset the output stream."""
        self.output_stream.seek(0)
        self.output_stream.truncate(0)


if __name__ == "__main__":
    unittest.main()
