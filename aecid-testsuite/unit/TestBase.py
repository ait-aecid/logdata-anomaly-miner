import unittest
import os
import shutil
import logging
import sys
from aminer import AminerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.events.StreamPrinterEventHandler import StreamPrinterEventHandler
from aminer.util import PersistenceUtil
from aminer.util import SecureOSFunctions
from _io import StringIO


def initialize_loggers(aminer_config, aminer_user, aminer_grp):
    """Initialize all loggers."""
    datefmt = '%d/%b/%Y:%H:%M:%S %z'

    persistence_dir = aminer_config.config_properties.get(AminerConfig.KEY_PERSISTENCE_DIR, AminerConfig.DEFAULT_PERSISTENCE_DIR)
    rc_logger = logging.getLogger(AminerConfig.REMOTE_CONTROL_LOG_NAME)
    rc_logger.setLevel(logging.DEBUG)
    remote_control_log_file = aminer_config.config_properties.get(
        AminerConfig.KEY_REMOTE_CONTROL_LOG_FILE, os.path.join(persistence_dir, AminerConfig.DEFAULT_REMOTE_CONTROL_LOG_FILE))
    try:
        rc_file_handler = logging.FileHandler(remote_control_log_file)
        shutil.chown(remote_control_log_file, aminer_user, aminer_grp)
    except OSError as e:
        print('Could not create or open %s: %s. Stopping..' % (remote_control_log_file, e), file=sys.stderr)
        sys.exit(1)
    rc_file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt=datefmt))
    rc_logger.addHandler(rc_file_handler)
    logging.addLevelName(15, "REMOTECONTROL")

    stat_logger = logging.getLogger(AminerConfig.STAT_LOG_NAME)
    stat_logger.setLevel(logging.INFO)
    stat_log_file = aminer_config.config_properties.get(
        AminerConfig.KEY_STAT_LOG_FILE, os.path.join(persistence_dir, AminerConfig.DEFAULT_STAT_LOG_FILE))
    try:
        stat_file_handler = logging.FileHandler(stat_log_file)
        shutil.chown(stat_log_file, aminer_user, aminer_grp)
    except OSError as e:
        print('Could not create or open %s: %s. Stopping..' % (stat_log_file, e), file=sys.stderr)
        sys.exit(1)
    stat_file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(message)s', datefmt=datefmt))
    stat_logger.addHandler(stat_file_handler)

    debug_logger = logging.getLogger(AminerConfig.DEBUG_LOG_NAME)
    if AminerConfig.DEBUG_LEVEL == 0:
        debug_logger.setLevel(logging.ERROR)
    elif AminerConfig.DEBUG_LEVEL == 1:
        debug_logger.setLevel(logging.INFO)
    else:
        debug_logger.setLevel(logging.DEBUG)
    debug_log_file = aminer_config.config_properties.get(
        AminerConfig.KEY_DEBUG_LOG_FILE, os.path.join(persistence_dir, AminerConfig.DEFAULT_DEBUG_LOG_FILE))
    try:
        debug_file_handler = logging.FileHandler(debug_log_file)
        shutil.chown(debug_log_file, aminer_user, aminer_grp)
    except OSError as e:
        print('Could not create or open %s: %s. Stopping..' % (debug_log_file, e), file=sys.stderr)
        sys.exit(1)
    debug_file_handler.setFormatter(logging.Formatter(fmt='%(asctime)s %(levelname)s %(message)s', datefmt=datefmt))
    debug_logger.addHandler(debug_file_handler)


# skipcq: PTC-W0046
class TestBase(unittest.TestCase):
    """This is the base class for all unittests."""

    __configFilePath = os.getcwd()+'/unit/config/config.py'

    def setUp(self):
        """Set up all needed variables and remove persisted data."""
        PersistenceUtil.persistable_components = []
        self.aminer_config = AminerConfig.load_config(self.__configFilePath)
        self.analysis_context = AnalysisContext(self.aminer_config)
        self.output_stream = StringIO()
        self.stream_printer_event_handler = StreamPrinterEventHandler(self.analysis_context, self.output_stream)
        persistence_dir_name = AminerConfig.build_persistence_file_name(self.aminer_config)
        if os.path.exists(persistence_dir_name):
            shutil.rmtree(persistence_dir_name)
        if not os.path.exists(persistence_dir_name):
            os.makedirs(persistence_dir_name)
        initialize_loggers(self.aminer_config, 'aminer', 'aminer')
        if isinstance(persistence_dir_name, str):
            persistence_dir_name = persistence_dir_name.encode()
        SecureOSFunctions.secure_open_base_directory(persistence_dir_name, os.O_RDONLY | os.O_DIRECTORY | os.O_PATH)
        PersistenceUtil.SKIP_PERSISTENCE_ID_WARNING = True

    def tearDown(self):
        """Delete all persisted data after the tests."""
        self.aminer_config = AminerConfig.load_config(self.__configFilePath)
        persistence_file_name = AminerConfig.build_persistence_file_name(self.aminer_config)
        if os.path.exists(persistence_file_name):
            shutil.rmtree(persistence_file_name)
        if not os.path.exists(persistence_file_name):
            os.makedirs(persistence_file_name)
        SecureOSFunctions.close_base_directory()

    def reset_output_stream(self):
        """Reset the output stream."""
        self.output_stream.seek(0)
        self.output_stream.truncate(0)


if __name__ == "__main__":
    unittest.main()
