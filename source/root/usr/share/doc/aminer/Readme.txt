Preamble:
=========

This document is the starting point to the user documentation.
For developer documentation start with "Design.txt".

The documentation attempts to strike out especially useful information
with following keywords.

CAVEAT: Keep that in mind using AMiner

PRODUCTION: This is a hint for production use


Installation Requirements:
==========================

* Python language compatibility:

Code is compatible with Python 2.6, software was tested on:

  * CentOS 6.7: Released 2015-08-07, Python 2.6.6
  * Ubuntu Xenial 1604: FIXME: Beta-Release, Python 2.???


* System requirements:

Requirements are depending on AMiner configuration.

  * Simple Logcheck-like operation: As opposed to logcheck, AMiner
    runs in stream-processing mode. For simple filtering 32MB RAM
    are sufficient.

  * Advanced operation: See documentation of analysis components
    configured to learn about memory requirements.


Concepts:
=========

* Alert: Alerts are generated when severe or numerous events where
  detected.

* Event: Events are triggered when unexpected log atoms are received
  or expected log atoms are missing.

* Log Atom: Log-data, that is always written as whole block by atomic
  logging operation. This can be a single syslog line or an XML-logger
  stanza.

* Parsing Model: Tree-like model describing the structure of log
  atoms on that system. The model could be seen as a single, very
  large regular expression modelling the log data. Thus computational
  complexity for log atom parsing is more like O(log(n)) than
  the O(n) when handling data with separate regular expressions.

* Detector Rules: Those rules select parsed log atoms according
  to their properties and facilitate interaction with the appropriate
  detectors. The rules for also tree-like structures to allow
  evaluation of the rules "A&B" and "A&C" with only a single check
  of property "A".


Features:
=========

This is a brief list of currently supported features. To learn
more about each feature, read "Design.txt".

* Daemon mode and foreground operation

* Privilege separation between logfile reading and analysis process

* Fast tree-shaped parsing model to extract features from log
  atoms. Currently supported data elements:
  * fixed strings
  * decimal/hex numbers
  * IP addresses
  * date and time fields
  * delimited fields
  * fixed alphabet fields

  Current structural elements:
  * sequences
  * branches
  * repeated elements
  * optional elements

* Very flexible pipeline design to:
  * analyse parsed data (see analyzers below)
  * split the stream, e.g. per host or per source zone

* Analysis components for event generation (see Analysis.txt):
  * Events on unknown (unparseable) log atoms
  * Events on log atoms with new structure, e.g. log atoms of
    type not observed before on this system
  * Detection of new items in lines (new MACs, IPs, hostnames,
    user names)
  * Histogram reports for given properties in any path or per
    path
  * Whitelisting of parsed atoms using complex rulesets
  * Statistical check if last n extracted values deviate from
    average previously observed
  * Event generation due to non-correlated log atoms

* Action components:
  * E-mail notifications


Following features are partially implemented:

* Persistence of analysis state between restarts


Getting Started:
================

* Test AMiner with generic configuration:

A good way to get knowing AMiner and its features is running it
in foreground on prerecorded data. You can start from the quite
empty template /etc/aminer/config.py.template or use one of the
demo configurations, e.g.
/usr/share/doc/aminer/demo/ubuntu-syslog-config.py.


CAVEAT: The demo file contains settings nice for demonstration
but unsuitable for production use! Use /etc/aminer/config.py.template
as a starting point instead!


You just can move your input file to analyze to "test.log", create
a directory "aminer" and run AMiner from that working directory
or you may adjust the demo configuration.

gzip -cd /usr/share/doc/aminer/demo/ubuntu-syslog-config.py.gz > config.py
/usr/bin/AMiner --Config config.py

On the first run you may notice, that AMiner will report detection
of numerous new path elements, e.g.

-------------------------------------------------------------------------------
New path /model/services/cron/pid  (1 lines)
  Feb  5 08:17:01 test.local CRON[11581]: (root) CMD (   cd / && run-parts --report /etc/cron.hourly)
  /model: None ('Feb  5 08:17:01 test.local CRON[11581]: (root) CMD (   cd / && run-parts --report /etc/cron.hourly)')
  /model/syslog: None ('Feb  5 08:17:01 test.local ')
    /model/syslog/time: 2015-02-05 08:17:01 ('Feb  5 08:17:01')
    /model/syslog/sp0:   (' ')
-------------------------------------------------------------------------------

Each of those reports corresponds to a structural property of
the parsed log line, that was not encountered before. But as the
the demo "ubuntu-syslog-config.py" is configured to report each
of that occurrences only once, you will see each path in this
run only once. When AMiner is terminated using [Ctrl]-C and started
again, it loads information about previously encountered items
from the persistence directory and will also not report again.


PRODUCTION: To avoid too many false reports when deploying AMiner
the first time, perform a run with "autoIncludeFlag=True" on the
current logfiles of the target system to and then toggle to "False".


Rule Based Checking Using Detector Rules:
=========================================

AMiner comes with a pattern matching rule engine for efficient
implementation of both whitelisting, blacklisting and correlation
approaches. See "demo/ubuntu-syslog-config.py" for rule examples.

The rules themselves can be used for whitelisting but also to
hook custom actions, e.g. to handle exclusions from whitelisting,
but also to forward events to correlation checking.

PRODUCTION: One featrure to increase performace is the "ParallelMatchRule".
While a normal "OrMatchRule" will match if any of the subrules
matches and then terminate the search, the parallel rule will
evaluate all "Or" branches, thus allowing parallelization of checks.
This makes only sense, when the different branches also make use
of "MatchActions" to act when one of the branches found a match.


Correlation Checking:
=====================

AMiner also allows whitelisting using time correlation of log
atoms. With central log aggregation, this can be done across services
and machines. This could be applied e.g. to following log lines:

  Feb  5 08:17:01 test.local CRON[11581]: (root) CMD (   cd / && run-parts --report /etc/cron.hourly)
  Feb 05 08:17:04 test.local CRON[11581]: pam_unix(cron:session): session closed for user root

Usually an event hidden inside the logics of one machine triggers
a set of other events, thus producing log-atoms as artefacts.
In the example log lines, this is the expiration of the a timer
within the cron daemon. This hidden event is denominated A*. It
then triggers event A, the syslog entry when starting a hourly
cronjob, thus producing the first artefact A. When the cron jobs
is completed, pam-library is invoked (hidden event B*), causing
writing of artefact B to "auth.log". As A* always causes A and B*
and B* always results in B, the artefacts A and B have to occur
in pairs.

  CAVEAT: The cause of events above does not imply, that A has
  to be seen before B. As A* is causing B in the end, depending
  on the delay A*->A and B*->B, B may be observed before A!

Matching will only happen, if A and B are close enough in time.
Thus a rule for the cronjobs above may report an anomaly if the
cron jobs run time is abnormally long.

Other examples for log lines to be correlated:

  * Each webserver access has to pass through a firewall before.
    Thus each webserver logline has to be preceeded by a firewall
    logline (vice versa is not true for bad internet: someone
    may only send single SYN-packet, thus causing firewall log
    but webserver will never receive a request).

  * Monitoring plugin logs on using SSH and then executes check
    command, logs out. Thus login artefact without check or logout
    in time is suspicious.

Implementation example:

-------------------------------------------------------------------------------
# Create a correlation rule: As syslog timestamps have only second
# precision and B usually is some ms after A, accept correlation
# only in range (0.0, 1.0) seconds.
  aImpliesBRule=TimeCorrelationViolationDetector.CorrelationRule(
      'A implies B', 0.0, 1.0, maxArtefactsAForSingleB=1,
      artefactMatchParameters=None)

# Build event selectors: As one selector may select an event that
# is input to more than one correlation rule, accept lists as input.
  aClassSelector=TimeCorrelationViolationDetector.EventClassSelector(
      'A-Event', [aImpliesBRule], None)
  bClassSelector=TimeCorrelationViolationDetector.EventClassSelector(
      'B-Event', None, [aImpliesBRule])

# Hook the selectors to the detector rules tree. 
...
  allRules.append(Rules.PathExistsMatchElement('/model/services/A', aClassSelector))
...
# Use the standard WhitelistViolationDetector but with parallel
# matching to a) perform whitelisting of acceptable log lines
# and b) forwarding of selected events to the correlation detectors.
  whitelistViolationDetector=WhitelistViolationDetector.WhitelistViolationDetector(
      [Rules.ParallelMatchRule(allRules)], anomalyEventHandlers)
-------------------------------------------------------------------------------

Artefact output would be:

-------------------------------------------------------------------------------
Correlation rule "A implies B" violated (1 lines)
  Jan 07 15:59:55 AAAAAA
  FAIL: "Jan 07 15:59:55 AAAAAA" (A-Event)
Historic examples:
  "Sep 15 17:31:57 AAAAAA" (A-Event) ==> "Sep 15 17:31:57 BBBBBB" (B-Event)
  "Jan 29 03:34:37 AAAAAA" (A-Event) ==> "Jan 29 03:34:38 BBBBBB" (B-Event)
  "May 13 03:39:39 AAAAAA" (A-Event) ==> "May 13 03:39:39 BBBBBB" (B-Event)
  "May 13 09:09:09 AAAAAA" (A-Event) ==> "May 13 09:09:10 BBBBBB" (B-Event)
  "May 20 06:21:37 AAAAAA" (A-Event) ==> "May 20 06:21:37 BBBBBB" (B-Event)
  "May 20 14:44:56 AAAAAA" (A-Event) ==> "May 20 14:44:57 BBBBBB" (B-Event)
  "May 25 03:35:42 AAAAAA" (A-Event) ==> "May 25 03:35:43 BBBBBB" (B-Event)
  "May 30 22:43:22 AAAAAA" (A-Event) ==> "May 30 22:43:22 BBBBBB" (B-Event)
  "Jun 03 17:18:49 AAAAAA" (A-Event) ==> "Jun 03 17:18:49 BBBBBB" (B-Event)
  "Jun 04 09:56:36 AAAAAA" (A-Event) ==> "Jun 04 09:56:36 BBBBBB" (B-Event)
-------------------------------------------------------------------------------


Running as a Service:
=====================

The package comes with an upstart and a systemd script to run
AMiner as a daemon. Those scripts are deactivated by default because:

* there is no AMiner default configuration, you need to generate
  it before starting anyway.

* CAVEAT: When AMiner is misconfigured and his diagnostic output
  somehow reaches the logfiles it is currently processing, a log
  data loop can be generated, just filling up your disks!

To enable AMiner daemon, do the following:

* Upstart: Enable autostart by uncommenting the "start on" stanza
  in "/etc/init/aminer.conf". As AMiner stdout/stderr messages
  would end up in "/var/log/upstart/aminer.log", there is no risk
  for log data loops UNLESS you include those files to be handled
  by AMiner or you have another type of data forwarding from the
  files to e.g. main syslog in place.

* Systemd: Service is enabled using "systemctl enable aminer".
  The default AMiner service configuration will write all messages
  from stdout/stderr to /dev/null due to "StandardOutput=null"
  setting to avoid log data loops. If you are sure what you are
  doing, you may want to change this to "StandardOutput=journal"
  and deactivate journal to syslog forwarding when you need to
  have aminer parse the syslog data also.
