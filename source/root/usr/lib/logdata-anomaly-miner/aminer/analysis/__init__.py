from aminer.analysis.MatchValueAverageChangeDetector import MatchValueAverageChangeDetector
from aminer.analysis.MatchValueStreamWriter import MatchValueStreamWriter
from aminer.analysis.MissingMatchPathValueDetector import MissingMatchPathValueDetector
from aminer.analysis.MissingMatchPathValueDetector import MissingMatchPathListValueDetector
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector
from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector
from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector
from aminer.analysis.TimeCorrelationDetector import TimeCorrelationDetector
from aminer.analysis.TimeCorrelationViolationDetector import TimeCorrelationViolationDetector
from aminer.analysis.TimestampsUnsortedDetector import TimestampsUnsortedDetector
from aminer.analysis.WhitelistViolationDetector import WhitelistViolationDetector
"""This file contains interface definition useful implemented by
classes in this directory and for use from code outside this
directory. All classes are defined in separate files, only the
namespace references are added here to simplify the code.

No generic interfaces here yet.

Add also the namespace references to classes defined in this
directory."""

CONFIG_KEY_LOG_LINE_PREFIX = 'LogPrefix'
