import unittest
import os
import shutil
import logging
import sys
import errno
import inspect
from aminer.AminerConfig import KEY_LOG_DIR, DEFAULT_LOG_DIR, KEY_PERSISTENCE_DIR, DEFAULT_PERSISTENCE_DIR, DEBUG_LOG_NAME,\
    KEY_REMOTE_CONTROL_LOG_FILE, KEY_STAT_LOG_FILE, KEY_DEBUG_LOG_FILE, REMOTE_CONTROL_LOG_NAME, DEFAULT_REMOTE_CONTROL_LOG_FILE,\
    STAT_LOG_NAME, DEFAULT_STAT_LOG_FILE, DEBUG_LEVEL, load_config, build_persistence_file_name, DEFAULT_DEBUG_LOG_FILE
from aminer.AnalysisChild import AnalysisContext
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from aminer.parsing.ModelElementInterface import ModelElementInterface
from aminer.parsing.MatchElement import MatchElement
from aminer.util import PersistenceUtil
from aminer.util import SecureOSFunctions
from _io import StringIO


def initialize_loggers(aminer_config, aminer_user_id, aminer_grp_id):
    """Initialize all loggers."""
    datefmt = '%d/%b/%Y:%H:%M:%S %z'

    log_dir = aminer_config.config_properties.get(KEY_LOG_DIR, DEFAULT_LOG_DIR)
    if log_dir == DEFAULT_LOG_DIR:
        try:
            if not os.path.isdir(log_dir):
                persistence_dir_path = aminer_config.config_properties.get(KEY_PERSISTENCE_DIR, DEFAULT_PERSISTENCE_DIR)
                persistence_dir_fd = SecureOSFunctions.secure_open_base_directory(persistence_dir_path)
                if SecureOSFunctions.base_dir_path == DEFAULT_PERSISTENCE_DIR:
                    relative_path_log_dir = os.path.split(DEFAULT_LOG_DIR)[1]
                    os.mkdir(relative_path_log_dir, dir_fd=persistence_dir_fd)
                    os.chown(relative_path_log_dir, aminer_user_id, aminer_grp_id, dir_fd=persistence_dir_fd, follow_symlinks=False)
        except OSError as e:
            if e.errno != errno.EEXIST:
                msg = 'Unable to create log-directory: %s' % log_dir
            else:
                msg = e
            logging.getLogger(DEBUG_LOG_NAME).error(msg.strip('\n'))
            print(msg, file=sys.stderr)

    tmp_value = aminer_config.config_properties.get(KEY_REMOTE_CONTROL_LOG_FILE)
    if tmp_value is not None and b'/' in tmp_value:
        print('%s attribute must not contain a full directory path, but only the filename.' % KEY_REMOTE_CONTROL_LOG_FILE,
              file=sys.stderr)
        sys.exit(1)
    tmp_value = aminer_config.config_properties.get(KEY_STAT_LOG_FILE)
    if tmp_value is not None and b'/' in tmp_value:
        print('%s attribute must not contain a full directory path, but only the filename.' % KEY_STAT_LOG_FILE, file=sys.stderr)
        sys.exit(1)
    tmp_value = aminer_config.config_properties.get(KEY_DEBUG_LOG_FILE)
    if tmp_value is not None and b'/' in tmp_value:
        print('%s attribute must not contain a full directory path, but only the filename.' % KEY_DEBUG_LOG_FILE, file=sys.stderr)
        sys.exit(1)

    log_dir_fd = SecureOSFunctions.secure_open_log_directory(log_dir, os.O_RDONLY | os.O_DIRECTORY | os.O_PATH)
    rc_logger = logging.getLogger(REMOTE_CONTROL_LOG_NAME)
    rc_logger.setLevel(logging.DEBUG)
    remote_control_log_file = aminer_config.config_properties.get(
        KEY_REMOTE_CONTROL_LOG_FILE, os.path.join(log_dir, DEFAULT_REMOTE_CONTROL_LOG_FILE))
    if not remote_control_log_file.startswith(log_dir):
        remote_control_log_file = os.path.join(log_dir, remote_control_log_file)
    try:
        rc_file_handler = logging.FileHandler(remote_control_log_file)
        os.chown(remote_control_log_file, aminer_user_id, aminer_grp_id, dir_fd=log_dir_fd, follow_symlinks=False)
    except OSError as e:
        print('Could not create or open %s: %s. Stopping..' % (remote_control_log_file, e), file=sys.stderr)
        sys.exit(1)
    rc_file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt=datefmt))
    rc_logger.addHandler(rc_file_handler)
    logging.addLevelName(15, "REMOTECONTROL")

    stat_logger = logging.getLogger(STAT_LOG_NAME)
    stat_logger.setLevel(logging.INFO)
    stat_log_file = aminer_config.config_properties.get(KEY_STAT_LOG_FILE, os.path.join(log_dir, DEFAULT_STAT_LOG_FILE))
    if not stat_log_file.startswith(log_dir):
        stat_log_file = os.path.join(log_dir, stat_log_file)
    try:
        stat_file_handler = logging.FileHandler(stat_log_file)
        os.chown(stat_log_file, aminer_user_id, aminer_grp_id, dir_fd=log_dir_fd, follow_symlinks=False)
    except OSError as e:
        print('Could not create or open %s: %s. Stopping..' % (stat_log_file, e), file=sys.stderr)
        sys.exit(1)
    stat_file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(message)s', datefmt=datefmt))
    stat_logger.addHandler(stat_file_handler)

    debug_logger = logging.getLogger(DEBUG_LOG_NAME)
    if DEBUG_LEVEL == 0:
        debug_logger.setLevel(logging.ERROR)
    elif DEBUG_LEVEL == 1:
        debug_logger.setLevel(logging.INFO)
    else:
        debug_logger.setLevel(logging.DEBUG)
    debug_log_file = aminer_config.config_properties.get(
        KEY_DEBUG_LOG_FILE, os.path.join(log_dir, DEFAULT_DEBUG_LOG_FILE))
    if not debug_log_file.startswith(log_dir):
        debug_log_file = os.path.join(log_dir, debug_log_file)
    try:
        debug_file_handler = logging.FileHandler(debug_log_file)
        os.chown(debug_log_file, aminer_user_id, aminer_grp_id, dir_fd=log_dir_fd, follow_symlinks=False)
    except OSError as e:
        print('Could not create or open %s: %s. Stopping..' % (debug_log_file, e), file=sys.stderr)
        sys.exit(1)
    debug_file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt=datefmt))
    debug_logger.addHandler(debug_file_handler)


# skipcq: PTC-W0046
class TestBase(unittest.TestCase):
    """This is the base class for all unittests."""

    def get_config_file_path(self):
        # example: logdata-anomaly-miner/aecid-testsuite/unit/analysis/AtomFiltersTest.py - we want to know the directory analysis.
        return os.getcwd()+'/unit/data/parallel_configs/%s_config.py' % inspect.getmodule(self).__file__.split("unit/")[1].split("/")[0]

    def setUp(self):
        """Set up all needed variables and remove persisted data."""
        PersistenceUtil.persistable_components = []
        self.aminer_config = load_config(self.get_config_file_path())
        self.analysis_context = AnalysisContext(self.aminer_config)
        self.output_stream = StringIO()
        self.stream_printer_event_handler = StreamPrinterEventHandler(self.analysis_context, self.output_stream)
        persistence_dir_name = build_persistence_file_name(self.aminer_config)
        if os.path.exists(persistence_dir_name):
            shutil.rmtree(persistence_dir_name)
        if not os.path.exists(persistence_dir_name):
            os.makedirs(persistence_dir_name)
        initialize_loggers(self.aminer_config, os.getuid(), os.getgid())
        if isinstance(persistence_dir_name, str):
            persistence_dir_name = persistence_dir_name.encode()
        SecureOSFunctions.secure_open_base_directory(persistence_dir_name, os.O_RDONLY | os.O_DIRECTORY | os.O_PATH)
        PersistenceUtil.SKIP_PERSISTENCE_ID_WARNING = True

    def tearDown(self):
        """Delete all persisted data after the tests."""
        self.aminer_config = load_config(self.get_config_file_path())
        persistence_file_name = build_persistence_file_name(self.aminer_config)
        if os.path.exists(persistence_file_name):
            shutil.rmtree(persistence_file_name)
        if not os.path.exists(persistence_file_name):
            os.makedirs(persistence_file_name)
        SecureOSFunctions.close_base_directory()

    def reset_output_stream(self):
        """Reset the output stream."""
        self.output_stream.seek(0)
        self.output_stream.truncate(0)

    def compare_match_results(self, data, match_element, match_context, id_, path, match_string, match_object, children):
        """Compare the results of get_match_element() if match_element is not None."""
        self.assertEqual(match_element.path, "%s/%s" % (path, id_))
        self.assertEqual(match_element.match_string, match_string)
        self.assertEqual(match_element.match_object, match_object)
        if children is None:
            self.assertIsNone(match_element.children, children)
        else:
            self.assertEqual(len(children), len(match_element.children))
            for i, child in enumerate(children):
                self.assertEqual(match_element.children[i].path, child.path)
                self.assertEqual(match_element.children[i].match_string, child.match_string)
                self.assertEqual(match_element.children[i].match_object, child.match_object)
                self.assertIsNone(match_element.children[i].children, children)
        self.assertEqual(match_context.match_string, match_string)
        self.assertEqual(match_context.match_data, data[len(match_string):])

    def compare_no_match_results(self, data, match_element, match_context):
        """Compare the results of get_match_element() if match_element is not None."""
        self.assertIsNone(match_element, None)
        self.assertEqual(match_context.match_data, data)


class DummyMatchContext:
    """Dummy class for MatchContext."""

    def __init__(self, match_data: bytes):
        """Initiate the Dummy class."""
        self.match_data = match_data
        self.match_string = b''

    def update(self, match_string: bytes):
        """Update the data."""
        self.match_data = self.match_data[len(match_string):]
        self.match_string += match_string


class DummyFixedDataModelElement(ModelElementInterface):
    """Dummy class for fixed string ModelElements."""

    def __init__(self, element_id: str, data: bytes):
        self.element_id = element_id
        self.data = data

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):  # skipcq: PYL-R0201
        """
        Get all possible child model elements of this element.
        @return None as there are no children of this element.
        """
        return None

    def get_match_element(self, path: str, match_context):
        """@return None when there is no match, MatchElement otherwise."""
        if not match_context.match_data.startswith(self.data):
            return None
        match_context.update(self.data)
        return MatchElement("%s/%s" % (path, self.element_id), self.data, self.data, None)


class DummyFirstMatchModelElement(ModelElementInterface):
    """This class defines a model element to return the match from the the first matching child model within a given list."""

    def __init__(self, element_id, children):
        self.element_id = element_id
        self.children = children
        if (children is None) or (None in children):
            msg = 'Invalid children list'
            logging.getLogger(DEBUG_LOG_NAME).error(msg)
            raise Exception(msg)

    def get_id(self):
        """Get the element ID."""
        return self.element_id

    def get_child_elements(self):
        """Get all possible child model elements of this element."""
        return self.children

    def get_match_element(self, path, match_context):
        """@return None when there is no match, MatchElement otherwise."""
        current_path = "%s/%s" % (path, self.element_id)

        match_data = match_context.match_data
        for child_element in self.children:
            child_match = child_element.get_match_element(current_path, match_context)
            if child_match is not None:
                return child_match
            match_context.match_data = match_data
        return None


if __name__ == "__main__":
    unittest.main()
