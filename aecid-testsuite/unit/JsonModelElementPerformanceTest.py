import unittest
from aminer.input.JsonStateMachine import json_machine
from unit.TestBase import TestBase
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from aminer.input.LogAtom import LogAtom
from aminer.AnalysisChild import AnalysisContext
from aminer.parsing.MatchContext import MatchContext
import time
import random
from time import process_time
from _io import StringIO
import timeit
import importlib


breakout = False
data = None
def found_json(_data):
    """Set the breakout variable if the JsonStateMachine finished."""
    global breakout
    breakout = True
    global data
    data = _data


class JsonModelElementPerformanceTest(TestBase):
    """These unittests test the performance of the JsonModelElement."""

    result_string = "The JsonModelElement could in average handle %d LogAtoms %s\n"
    result = ""
    iterations = 10
    waiting_time = 1
    state = json_machine(found_json)
    log_atoms = []

    @classmethod
    def tearDownClass(cls):
        """Run the TestBase tearDownClass method and print the results."""
        super(JsonModelElementPerformanceTest, cls).tearDownClass()
        print("\nwaiting time: %d seconds" % cls.waiting_time)
        print(cls.result)

    def setUp(self):
        """Set up needed variables."""
        TestBase.setUp(self)
        self.output_stream = StringIO()
        self.stream_printer_event_handler = StreamPrinterEventHandler(self.analysis_context, self.output_stream)
        global breakout
        breakout = False
        global data
        data = None
        self.state = json_machine(found_json)

    @staticmethod
    def run_test(json_me, json_data):
        for d in json_data:
            json_me.get_match_element("path", MatchContext(d))

    def test1_aminer_demo_data(self):
        """Run the performance tests with the output of the aminer demo."""
        with open("demo/aminerJsonInputDemo/json_logs/aminer.log", "rb") as f:
            stream_data = f.read()
        spec = importlib.util.spec_from_file_location("aminer_config", "/usr/lib/logdata-anomaly-miner/aminer/YamlConfig.py")
        aminer_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(aminer_config)
        aminer_config.load_yaml("demo/aminerJsonInputDemo/json-aminer-demo.yml")
        yml_context = AnalysisContext(aminer_config)
        yml_context.build_analysis_pipeline()
        json_me = yml_context.atomizer_factory.parsing_model
        json_data = []
        global breakout
        global data
        while len(stream_data) > 0:
            i = 0
            for i, char in enumerate(stream_data):
                self.state = self.state(char)
                if breakout or self.state is None:
                    json_data.append(stream_data[:i+1])
                    breakout = False
                    data = None
                    self.state = json_machine(found_json)
                    break
            stream_data = stream_data[i+1:]
        results = [None] * self.iterations
        avg = 0
        z = 0
        while z < self.iterations:
            #result = self.waiting_time / (timeit.timeit(lambda: self.run_test(json_me, json_data), number=1) / 1)
            result = self.waiting_time / (timeit.timeit(lambda: self.run_test(json_me, json_data), number=10) / 10)
            results[z] = int(result * len(json_data))
            z = z + 1
            avg = avg + result * len(json_data)
        avg = int(avg / self.iterations)
        type(self).result = self.result + self.result_string % (avg, results)


if __name__ == "__main__":
    unittest.main()
