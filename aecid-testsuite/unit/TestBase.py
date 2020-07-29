import unittest
import os
import shutil
from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from _io import StringIO


class TestBase(unittest.TestCase):
    __configFilePath = os.getcwd()+'/unit/config/config.py'

    def setUp(self):
        self.aminer_config = AMinerConfig.load_config(self.__configFilePath)
        self.analysis_context = AnalysisContext(self.aminer_config)
        self.output_stream = StringIO()
        self.stream_printer_event_handler = StreamPrinterEventHandler(self.analysis_context, self.output_stream)
        persistence_file_name = AMinerConfig.build_persistence_file_name(self.aminer_config)
        if os.path.exists(persistence_file_name):
            shutil.rmtree(persistence_file_name)
        if not os.path.exists(persistence_file_name):
            os.makedirs(persistence_file_name)

    def tearDown(self):
        self.aminer_config = AMinerConfig.load_config(self.__configFilePath)
        persistence_file_name = AMinerConfig.build_persistence_file_name(self.aminer_config)
        if os.path.exists(persistence_file_name):
            shutil.rmtree(persistence_file_name)
        if not os.path.exists(persistence_file_name):
            os.makedirs(persistence_file_name)

    def reset_output_stream(self):
        self.output_stream.seek(0)
        self.output_stream.truncate(0)


if __name__ == "__main__":
    unittest.main()
