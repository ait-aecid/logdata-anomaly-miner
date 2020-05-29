This document contains step by step instructions on what needs to be done 
to fully support a new Detector in the AMinerRemoteControl.

- add the Detector class to the exec_locals in the AnalysisChildRemoteControlHandler class.
The format needs to be 'NewDetector':aminer.analysis.NewDetector.

- if the class supports whitelisting events add it to the checks of the
AMinerRemoteControlExecutionMethods.whitelist_event_in_component method.
