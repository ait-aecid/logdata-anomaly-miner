"""This file contains interface definition useful implemented by classes in this directory and for use from code outside this
directory. All classes are defined in separate files, only the namespace references are added here to simplify the code.

No generic interfaces here yet.

Add also the namespace references to classes defined in this directory."""

CONFIG_KEY_LOG_LINE_PREFIX = 'LogPrefix'

from aminer.analysis.AtomFilters import MatchPathFilter, MatchValueFilter, SubhandlerFilter  # skipcq: FLK-E402
from aminer.analysis.EnhancedNewMatchPathValueComboDetector import EnhancedNewMatchPathValueComboDetector  # skipcq: FLK-E402
from aminer.analysis.EventCorrelationDetector import EventCorrelationDetector  # skipcq: FLK-E402
from aminer.analysis.EventTypeDetector import EventTypeDetector  # skipcq: FLK-E402
# skipcq: FLK-E402
from aminer.analysis.HistogramAnalysis import HistogramAnalysis, LinearNumericBinDefinition, ModuloTimeBinDefinition,\
    PathDependentHistogramAnalysis
from aminer.analysis.MatchFilter import MatchFilter  # skipcq: FLK-E402
from aminer.analysis.MatchValueAverageChangeDetector import MatchValueAverageChangeDetector  # skipcq: FLK-E402
from aminer.analysis.MatchValueStreamWriter import MatchValueStreamWriter  # skipcq: FLK-E402
from aminer.analysis.MissingMatchPathValueDetector import MissingMatchPathValueDetector  # skipcq: FLK-E402
from aminer.analysis.MissingMatchPathValueDetector import MissingMatchPathListValueDetector  # skipcq: FLK-E402
from aminer.analysis.NewMatchIdValueComboDetector import NewMatchIdValueComboDetector  # skipcq: FLK-E402
from aminer.analysis.NewMatchPathDetector import NewMatchPathDetector  # skipcq: FLK-E402
from aminer.analysis.NewMatchPathValueComboDetector import NewMatchPathValueComboDetector  # skipcq: FLK-E402
from aminer.analysis.NewMatchPathValueDetector import NewMatchPathValueDetector  # skipcq: FLK-E402
from aminer.analysis.ParserCount import ParserCount  # skipcq: FLK-E402
# skipcq: FLK-E402
from aminer.analysis.Rules import AndMatchRule, OrMatchRule, AtomFilterMatchAction, DebugHistoryMatchRule, EventGenerationMatchAction,\
    DebugMatchRule, IPv4InRFC1918MatchRule, ModuloTimeMatchRule, NegationMatchRule, ParallelMatchRule, PathExistsMatchRule,\
    StringRegexMatchRule, ValueDependentDelegatedMatchRule, ValueDependentModuloTimeMatchRule, ValueListMatchRule, ValueMatchRule,\
    ValueRangeMatchRule
from aminer.analysis.TimeCorrelationDetector import TimeCorrelationDetector  # skipcq: FLK-E402
# skipcq: FLK-E402
from aminer.analysis.TimeCorrelationViolationDetector import TimeCorrelationViolationDetector, CorrelationRule, EventClassSelector
from aminer.analysis.TimestampCorrectionFilters import SimpleMonotonicTimestampAdjust  # skipcq: FLK-E402
from aminer.analysis.TimestampsUnsortedDetector import TimestampsUnsortedDetector  # skipcq: FLK-E402
from aminer.analysis.VariableTypeDetector import VariableTypeDetector  # skipcq: FLK-E402
from aminer.analysis.WhitelistViolationDetector import WhitelistViolationDetector  # skipcq: FLK-E402
