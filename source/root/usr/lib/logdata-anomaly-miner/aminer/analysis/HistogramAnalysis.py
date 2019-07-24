"""This component performs a histogram analysis on one or more input
properties. The properties are parsed values denoted by their
parsing path. Those values are then handed over to the selected
"binning function", that calculates the histogram bin.

* Binning:

Binning can be done using one of the predefined binning functions
or by creating own subclasses from "HistogramAnalysis.BinDefinition".

  * LinearNumericBinDefinition: Binning function working on numeric
    values and sorting them into bins of same size.

  * ModuloTimeBinDefinition: Binning function working on parsed
    datetime values but applying a modulo function to them. This
    is useful for analysis of periodic activities.


* Example:

The following example creates a HistogramAnalysis using only the
property "/model/line/time", binned on per-hour basis and sending
a report every week:

  from aminer.analysis import HistogramAnalysis
  # Use a time-modulo binning function
  moduloTimeBinDefinition=HistogramAnalysis.ModuloTimeBinDefinition(
      3600*24, # Modulo values in seconds (1 day)
      3600,    # Division factor to get down to reporting unit (1h)
      0,       # Start of lowest bin
      1,       # Size of bin in reporting units
      24,      # Number of bins
      False)   # Disable outlier bins, not possible with time modulo
  histogramAnalysis=HistogramAnalysis.HistogramAnalysis(
      aminerConfig,
      [('/model/line/time', moduloTimeBinDefinition)],
      3600*24*7,  # Reporting interval (weekly)
      reportEventHandlers,        # Send report to those handlers
      resetAfterReportFlag=True)  # Zero counters after sending of report
  # Send the appropriate input feed to the component
  atomFilter.addHandler(histogramAnalysis)
"""

import time
from datetime import datetime

from aminer import AMinerConfig
from aminer.AnalysisChild import AnalysisContext
from aminer.input import AtomHandlerInterface
from aminer.util import PersistencyUtil
from aminer.util import TimeTriggeredComponentInterface


binomialTest = None
try:
  from scipy import stats
  binomialTest = stats.binom_test
except:
  pass


class BinDefinition(object):
  """This class defines the bins of the histogram."""
  def __init__(self):
    raise Exception('Not implemented')

  def hasOutlierBins(self):
    """Report if this binning works with outlier bins, that are
    bins for all values outside the normal binning range. If not,
    outliers are discarded. When true, the outlier bins are the
    first and last bin."""
    raise Exception('Not implemented')

  def getBinNames(self):
    """Get the names of the bins for reporting, including the
    outlier bins if any."""
    raise Exception('Not implemented')

  def getBin(self, value):
    """Get the number of the bin this value should belong to.
    @return the bin number or None if the value is an outlier
    and outlier bins were not requested. With outliers, bin 0
    is the bin with outliers below limit, first normal bin is
    at index 1."""
    raise Exception('Not implemented')

  def getBinPValue(self, binPos, totalValues, binValues):
    """Calculate a p-Value, how likely the observed number of
    elements in this bin is.
    @return the value or None when not applicable."""
    return None


class LinearNumericBinDefinition(BinDefinition):
  """This class defines the linear numeric bins."""
  def __init__(self, lowerLimit, binSize, binCount, outlierBinsFlag=False):
    self.lowerLimit = lowerLimit
    self.binSize = binSize
    self.binCount = binCount
    self.outlierBinsFlag = outlierBinsFlag
    self.binNames = None
    self.expectedBinRatio = 1.0/float(binCount)

  def hasOutlierBins(self):
    """Report if this binning works with outlier bins, that are
    bins for all values outside the normal binning range. If not,
    outliers are discarded. When true, the outlier bins are the
    first and last bin."""
    return self.outlierBinsFlag

  def getBinNames(self):
    """Get the names of the bins for reporting, including the
    outlier bins if any."""
# Cache the names here so that multiple histograms using same
# BinDefinition do not use separate copies of the strings.
    if self.binNames != None:
      return self.binNames
    self.binNames = []
    if self.outlierBinsFlag:
      self.binNames.append('...-%s)' % self.lowerLimit)
    start = self.lowerLimit
    for binPos in range(1, self.binCount+1):
      end = self.lowerLimit+binPos*self.binSize
      self.binNames.append('[%s-%s)' % (start, end))
      start = end
    if self.outlierBinsFlag:
      self.binNames.append('[%s-...' % start)
    return self.binNames

  def getBin(self, value):
    """Get the number of the bin this value should belong to.
    @return the bin number or None if the value is an outlier
    and outlier bins were not requested. With outliers, bin 0
    is the bin with outliers below limit, first normal bin is
    at index 1."""
    if self.outlierBinsFlag:
      if value < self.lowerLimit:
        return 0
      pos = int((value-self.lowerLimit)/self.binSize)
      if pos < self.binCount:
        return pos+1
      return self.binCount+1
    else:
      if value < self.lowerLimit:
        return None
      pos = int((value-self.lowerLimit)/self.binSize)
      if pos < self.binCount:
        return pos
      return None

  def getBinPValue(self, binPos, totalValues, binValues):
    """Calculate a p-Value, how likely the observed number of
    elements in this bin is.
    @return the value or None when not applicable."""
    if binomialTest is None:
      return None
    if self.outlierBinsFlag:
      if (binPos == 0) or (binPos > self.binCount):
        return None
    return binomialTest(binValues, totalValues, self.expectedBinRatio)


class ModuloTimeBinDefinition(LinearNumericBinDefinition):
  """This class defines the module time bins."""
  def __init__(self, moduloValue, timeUnit, lowerLimit, binSize, binCount,
               outlierBinsFlag=False):
    super(ModuloTimeBinDefinition, self).__init__(lowerLimit, \
        binSize, binCount, outlierBinsFlag)
    self.moduloValue = moduloValue
    self.timeUnit = timeUnit

  def getBin(self, value):
    """Get the number of the bin this value should belong to.
    @return the bin number or None if the value is an outlier
    and outlier bins were not requested. With outliers, bin 0
    is the bin with outliers below limit, first normal bin is
    at index 1."""
    timeValue = (value[1]%self.moduloValue)/self.timeUnit
    return super(ModuloTimeBinDefinition, self).getBin(timeValue)


class HistogramData():
  """This class defines the properties of one histogram to create
  and performs the accounting and reporting. When the Python scipy
  package is available, reports will also include probability
  score created using binomial testing."""
  def __init__(self, propertyPath, binDefinition):
    """Create the histogram data structures.
    @param lowerLimit the lowest value included in the first bin."""
    self.propertyPath = propertyPath
    self.binDefinition = binDefinition
    self.binNames = binDefinition.getBinNames()
    self.binData = [0]*(len(self.binNames))
    self.hasOutlierBinsFlag = binDefinition.hasOutlierBins()
    self.totalElements = 0
    self.binnedElements = 0

  def addValue(self, value):
    """Add one value to the histogram."""
    binPos = self.binDefinition.getBin(value)
    self.binData[binPos] += 1
    self.totalElements += 1
    if (self.hasOutlierBinsFlag) and (binPos != 0) and (binPos+1 != len(self.binNames)):
      self.binnedElements += 1

  def reset(self):
    """Remove all values from this histogram."""
    self.totalElements = 0
    self.binnedElements = 0
    self.binData = [0]*(len(self.binData))

  def clone(self):
    """Clone this object so that calls to addValue do not influence
    the old object any more. This behavior is a mixture of shallow
    and deep copy."""
    histogramData = HistogramData(self.propertyPath, self.binDefinition)
    histogramData.binNames = self.binNames
    histogramData.binData = self.binData[:]
    histogramData.totalElements = self.totalElements
    histogramData.binnedElements = self.binnedElements
    return histogramData

  def toString(self, indent):
    """Get a string representation of this histogram."""
    result = '%sProperty "%s" (%d elements):' % (indent, self.propertyPath, self.totalElements)
    fElements = float(self.totalElements)
    baseElement = self.binnedElements if self.hasOutlierBinsFlag else self.totalElements
    for binPos in range(0, len(self.binData)):
      count = self.binData[binPos]
      if count == 0:
        continue
      pValue = self.binDefinition.getBinPValue(binPos, baseElement, count)
      if pValue is None:
        result += '\n%s* %s: %d (ratio = %.2e)' % (indent, self.binNames[binPos], \
            count, float(count)/fElements)
      else:
        result += '\n%s* %s: %d (ratio = %.2e, p = %.2e)' % (indent, \
              self.binNames[binPos], count, float(count)/fElements, \
              pValue)
    return result


class HistogramAnalysis(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class creates a histogram for one or more properties
  extracted from a parsed atom."""

  def __init__(self, analysisContext, histogramDefs, reportInterval,
               reportEventHandlers, resetAfterReportFlag=True,
               persistenceId='Default'):
    """Initialize the analysis component.
    @param histogramDefs is a list of tuples containing the target
    property path to analyze and the BinDefinition to apply for
    binning.
    @param reportInterval delay in seconds between creation of two
    reports. The parameter is applied to the parsed record data
    time, not the system time. Hence reports can be delayed when
    no data is received."""
    self.lastReportTime = None
    self.nextReportTime = 0.0
    self.histogramData = []
    for (path, binDefinition) in histogramDefs:
      self.histogramData.append(HistogramData(path, binDefinition))
    self.reportInterval = reportInterval
    self.reportEventHandlers = reportEventHandlers
    self.resetAfterReportFlag = resetAfterReportFlag
    self.persistenceId = persistenceId
    self.nextPersistTime = None
    self.analysisContext = analysisContext
    aminerConfig = analysisContext.aminerConfig

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName = AMinerConfig.buildPersistenceFileName(
        aminerConfig, 'HistogramAnalysis', persistenceId)
    persistenceData = PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData != None:
      raise Exception('No data reading, def merge yet')


  def receiveAtom(self, logAtom):
    matchDict = logAtom.parserMatch.getMatchDictionary()
    dataUpdatedFlag = False
    for dataItem in self.histogramData:
      match = matchDict.get(dataItem.propertyPath, None)
      if match is None:
        continue
      dataUpdatedFlag = True
      dataItem.addValue(match.matchObject)

    timestamp = logAtom.getTimestamp()
    if self.nextReportTime < timestamp:
      if self.lastReportTime is None:
        self.lastReportTime = timestamp
        self.nextReportTime = timestamp+self.reportInterval
      else:
        self.sendReport(logAtom, timestamp)

    if (self.nextPersistTime is None) and (dataUpdatedFlag):
      self.nextPersistTime = time.time()+600


  def getTimeTriggerClass(self):
    """Get the trigger class this component should be registered
    for. This trigger is used only for persistency, so real-time
    triggering is needed."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def doTimer(self, triggerTime):
    """Check current ruleset should be persisted"""
    if self.nextPersistTime is None:
      return 600

    delta = self.nextPersistTime-triggerTime
    if delta < 0:
      self.doPersist()
      delta = 600
    return delta


  def doPersist(self):
    """Immediately write persistence data to storage."""
#    PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.nextPersistTime = None


  def sendReport(self, logAtom, timestamp):
    """Sends a report to the event handlers."""
    reportStr = 'Histogram report '
    if self.lastReportTime is not None:
      reportStr += 'from %s ' % datetime.fromtimestamp(self.lastReportTime).strftime("%Y-%m-%d %H:%M:%S")
    reportStr += 'till %s' % datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    reportStr = [reportStr]
    for dataItem in self.histogramData:
      for line in dataItem.toString('  ').split('\n'):
        reportStr.append(line)
    for listener in self.reportEventHandlers:
      listener.receiveEvent('Analysis.%s' % self.__class__.__name__,
                            'Histogram report', reportStr, logAtom, self)
    if self.resetAfterReportFlag:
      for dataItem in self.histogramData:
        dataItem.reset()

    self.lastReportTime = timestamp
    self.nextReportTime = timestamp+self.reportInterval


class PathDependentHistogramAnalysis(AtomHandlerInterface, TimeTriggeredComponentInterface):
  """This class provides a histogram analysis for only one property
  but separate histograms for each group of correlated match pathes.
  Assume there two pathes that include the requested property
  but they separate after the property was found on the path.
  Then objects of this class will produce 3 histograms: one for
  common path part including all occurences of the target property
  and one for each separate subpath, counting only those property
  values where the specific subpath was followed."""

  def __init__(self, analysisContext, propertyPath, binDefinition,
               reportInterval, reportEventHandlers, resetAfterReportFlag=True,
               persistenceId='Default'):
    """Initialize the analysis component.
    @param reportInterval delay in seconds between creation of two
    reports. The parameter is applied to the parsed record data
    time, not the system time. Hence reports can be delayed when
    no data is received."""
    self.lastReportTime = None
    self.nextReportTime = 0.0
    self.propertyPath = propertyPath
    self.binDefinition = binDefinition
    self.histogramData = {}
    self.reportInterval = reportInterval
    self.reportEventHandlers = reportEventHandlers
    self.resetAfterReportFlag = resetAfterReportFlag
    self.persistenceId = persistenceId
    self.nextPersistTime = None
    self.analysisContext = analysisContext
    aminerConfig = analysisContext.aminerConfig

    PersistencyUtil.addPersistableComponent(self)
    self.persistenceFileName = AMinerConfig.buildPersistenceFileName(
        aminerConfig, 'PathDependentHistogramAnalysis', persistenceId)
    persistenceData = PersistencyUtil.loadJson(self.persistenceFileName)
    if persistenceData is not None:
      raise Exception('No data reading, def merge yet')


  def receiveAtom(self, logAtom):
    matchDict = logAtom.parserMatch.getMatchDictionary()

    match = matchDict.get(self.propertyPath, None)
    if match is None:
      return
    matchValue = match.matchObject

    allPathSet = set(matchDict.keys())
    unmappedPath = []
    missingPathes = set()
    while allPathSet:
      path = allPathSet.pop()
      histogramMapping = self.histogramData.get(path, None)
      if histogramMapping is None:
        unmappedPath.append(path)
        continue
# So the path is already mapped to one histogram. See if all pathes
# to the given histogram are still in allPathSet. If not, a split
# within the mapping is needed.
      for mappedPath in histogramMapping[0]:
        try:
          allPathSet.remove(mappedPath)
        except:
          if mappedPath != path:
            missingPathes.add(mappedPath)
      if not missingPathes:
# Everything OK, just add the value to the mapping.
        histogramMapping[1].addValue(matchValue)
        histogramMapping[2] = logAtom.parserMatch
      else:
# We need to split the current set here. Keep the current statistics
# for all the missingPathes but clone the data for the remaining
# pathes.
        newHistogram = histogramMapping[1].clone()
        newHistogram.addValue(matchValue)
        newPathSet = histogramMapping[0]-missingPathes
        newHistogramMapping = [newPathSet, newHistogram, logAtom.parserMatch]
        for mappedPath in newPathSet:
          self.histogramData[mappedPath] = newHistogramMapping
        histogramMapping[0] = missingPathes
        missingPathes = set()

    if unmappedPath:
      histogram = HistogramData(self.propertyPath, self.binDefinition)
      histogram.addValue(matchValue)
      newRecord = [set(unmappedPath), histogram, logAtom.parserMatch]
      for path in unmappedPath:
        self.histogramData[path] = newRecord

    timestamp = logAtom.getTimestamp()
    if self.nextReportTime < timestamp:
      if self.lastReportTime is None:
        self.lastReportTime = timestamp
        self.nextReportTime = timestamp+self.reportInterval
      else:
        self.sendReport(logAtom, timestamp)

    if self.nextPersistTime is None:
      self.nextPersistTime = time.time()+600


  def getTimeTriggerClass(self):
    """Get the trigger class this component should be registered
    for. This trigger is used only for persistency, so real-time
    triggering is needed."""
    return AnalysisContext.TIME_TRIGGER_CLASS_REALTIME

  def doTimer(self, triggerTime):
    """Check current ruleset should be persisted"""
    if self.nextPersistTime is None:
      return 600

    delta = self.nextPersistTime-triggerTime
    if delta < 0:
      self.doPersist()
      delta = 600
    return delta


  def doPersist(self):
    """Immediately write persistence data to storage."""
#   PersistencyUtil.storeJson(self.persistenceFileName, list(self.knownPathSet))
    self.nextPersistTime = None


  def sendReport(self, logAtom, timestamp):
    """Send report to event handlers."""
    reportStr = 'Path histogram report '
    if self.lastReportTime != None:
      reportStr += 'from %s ' % datetime.fromtimestamp(self.lastReportTime).strftime("%Y-%m-%d %H:%M:%S")
    reportStr += 'till %s' % datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    reportStr = [reportStr]
    allPathSet = set(self.histogramData.keys())
    while allPathSet:
      path = allPathSet.pop()
      histogramMapping = self.histogramData.get(path)
      for path in histogramMapping[0]:
        allPathSet.discard(path)
      reportStr.append('Path values "%s":' % '", "'.join(histogramMapping[0]))
      reportStr.append('Example: %s' % histogramMapping[2].matchElement.matchString)
      for line in histogramMapping[1].toString('  ').split('\n'):
        reportStr.append('%s' % line) 
      if self.resetAfterReportFlag:
        histogramMapping[1].reset()
    for listener in self.reportEventHandlers:
      listener.receiveEvent('Analysis.%s' % self.__class__.__name__, \
          'Histogram report', reportStr, logAtom, self)

    self.lastReportTime = timestamp
    self.nextReportTime = timestamp+self.reportInterval
