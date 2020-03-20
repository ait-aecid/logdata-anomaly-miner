This document contains step by step instructions on what needs to be done 
to fully support a new Detector in the AMinerRemoteControl.

- add the Detector class to the execLocals in the AnalysisChildRemoteControlHandler class.
The format needs to be 'NewDetector':aminer.analysis.NewDetector.

- if the class supports whitelisting events add it to the checks of the
AMinerRemoteControlExecutionMethods.whitelistEventInComponent method.