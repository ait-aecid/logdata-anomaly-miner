import time
import zmq
from aminer.events.JsonConverterHandler import JsonConverterHandler
from aminer.events.ZmqEventHandler import ZmqEventHandler
from aminer.input.LogAtom import LogAtom
from aminer.parsing.ParserMatch import ParserMatch
from unit.TestBase import TestBase, DummyFixedDataModelElement, DummyMatchContext


class ZmqEventHandlerTest(TestBase):
    """Unittests for the ZmqEventHandler."""
    resource_name = b"testresource"
    sub_url = "tcp://localhost:5555"
    pub_url = "tcp://*:5555"
    topic = "test_topic"
    persistence_id = "Default"
    match_context = DummyMatchContext(b" pid=")
    fdme = DummyFixedDataModelElement("s1", b" pid=")
    match_element = fdme.get_match_element("", match_context)

    @classmethod
    def setUpClass(cls):
        """Start a ZmqConsumer."""
        cls.context = zmq.Context()
        cls.consumer = cls.context.socket(zmq.SUB)
        cls.consumer.setsockopt(zmq.RCVTIMEO, 500)
        cls.consumer.connect(cls.sub_url)
        cls.consumer.setsockopt_string(zmq.SUBSCRIBE, cls.topic)

    @classmethod
    def tearDownClass(cls):
        """Shutdown the ZmqConsumer."""
        cls.consumer.close()
        cls.context.destroy()

    def test1receive_event(self):
        """Test if events are processed correctly and that edge cases are caught in exceptions."""
        description = "jsonConverterHandlerDescription"
        test_detector = "Analysis.TestDetector"
        event_message = "An event happened!"
        sorted_log_lines = ["Event happened at /path/ 5 times.", "", "", "", ""]
        exp = '{\n  "AnalysisComponent": {\n    "AnalysisComponentIdentifier": 0,\n    "AnalysisComponentType": "%s",\n    ' \
              '"AnalysisComponentName": "%s",\n    "Message": "%s",\n    "PersistenceFileName": "%s",\n    "AffectedParserPaths": [\n' \
              '      "test/path/1",\n      "test/path/2"\n    ],\n    "LogResource": "testresource"\n  },\n  "LogData": {\n    ' \
              '"RawLogData": [\n      " pid="\n    ],\n    "Timestamps": [\n      %s\n    ],\n    "DetectionTimestamp": %s,\n    "LogLinesCount": 5\n  }%s\n}\n'
        jch = JsonConverterHandler([self.stream_printer_event_handler], self.analysis_context)
        t = round(time.time(), 3)
        log_atom = LogAtom(self.fdme.data, ParserMatch(self.match_element), t, self)
        self.analysis_context.register_component(self, description)
        event_data = {"AnalysisComponent": {"AffectedParserPaths": ["test/path/1", "test/path/2"]}}
        jch.receive_event(test_detector, event_message, sorted_log_lines, event_data, log_atom, self)
        output = self.output_stream.getvalue()
        zeh = ZmqEventHandler(self.analysis_context, self.topic, self.pub_url)
        self.assertTrue(zeh.receive_event(test_detector, event_message, sorted_log_lines, output, log_atom, self))
        topic = self.consumer.recv_string()
        self.assertEqual(self.topic, topic)
        val = self.consumer.recv_string()
        if val.endswith("\n\n"):
            val = val[:-1]
        detection_timestamp = None
        for line in val.split('\n'):
            if "DetectionTimestamp" in line:
                detection_timestamp = line.split(":")[1].strip(" ,")
                break
        self.assertEqual(val, exp % (self.__class__.__name__, description, event_message, self.persistence_id, round(t, 2), detection_timestamp, ""))

        # test output_event_handlers
        self.output_event_handlers = []
        self.assertTrue(zeh.receive_event(test_detector, event_message, sorted_log_lines, output, log_atom, self))
        self.assertRaises(zmq.error.Again, self.consumer.recv_string)

        self.output_event_handlers = [zeh]
        self.assertTrue(zeh.receive_event(test_detector, event_message, sorted_log_lines, output, log_atom, self))
        topic = self.consumer.recv_string()
        self.assertEqual(self.topic, topic)
        val = self.consumer.recv_string()
        if val.endswith("\n\n"):
            val = val[:-1]
        detection_timestamp = None
        for line in val.split("\n"):
            if "DetectionTimestamp" in line:
                detection_timestamp = line.split(":")[1].strip(" ,")
                break
        self.assertEqual(val, exp % (self.__class__.__name__, description, event_message, self.persistence_id, round(t, 2), detection_timestamp, ""))

        # test suppress detector list
        self.output_event_handlers = None
        self.analysis_context.suppress_detector_list = [description]
        self.assertTrue(zeh.receive_event(test_detector, event_message, sorted_log_lines, output, log_atom, self))
        self.assertRaises(zmq.error.Again, self.consumer.recv_string)

        self.output_event_handlers = [zeh]
        self.analysis_context.suppress_detector_list = []
        zeh.producer.close()
        self.assertFalse(zeh.receive_event(test_detector, event_message, sorted_log_lines, output, log_atom, self))
        zeh.context.destroy()

    def test2validate_parameters(self):
        """Test all initialization parameters for the event handler. Input parameters must be validated in the class."""
        t = round(time.time(), 3)
        log_atom = LogAtom(self.fdme.data, ParserMatch(self.match_element), t, self)
        zmq_event_handler = ZmqEventHandler(self.analysis_context, self.topic, self.pub_url)
        self.assertFalse(zmq_event_handler.receive_event("test_detector", "event_message", ["loglines", ""], 123, log_atom, self))
        zmq_event_handler.producer.close()
        zmq_event_handler.context.destroy()

        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, ["default"], self.pub_url)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, None, self.pub_url)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, b"Default", self.pub_url)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, True, self.pub_url)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, 123, self.pub_url)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, 123.3, self.pub_url)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, {"id": "Default"}, self.pub_url)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, (), self.pub_url)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, set(), self.pub_url)

        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, self.topic, None)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, self.topic, True)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, self.topic, 123)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, self.topic, 123.3)
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, self.topic, {"id": "Default"})
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, self.topic, ())
        self.assertRaises(TypeError, ZmqEventHandler, self.analysis_context, self.topic, set())
        self.assertRaises(ValueError, ZmqEventHandler, self.analysis_context, self.topic, "")
        self.assertRaises(ValueError, ZmqEventHandler, self.analysis_context, self.topic, b"")
        zmq_event_handler = ZmqEventHandler(self.analysis_context, self.topic, b"tcp://*:5555")
        zmq_event_handler.producer.close()
        zmq_event_handler.context.destroy()


if __name__ == "__main__":
    unittest.main()
