========
Overview
========

The logdata-anomaly-miner can be configured in two different formats: **yaml** and **python**. The preferred format is yaml and the default configuration file for it is */etc/aminer/config.yaml*. The python format can be configured in */etc/aminer/config..py* and offers more different ways to configure the logdata-anomaly-miner. However, this is only recommended for experts, as no errors are caught in the python configuration, which can make debugging very difficult. For both formats there are template configurations in */etc/aminer/template\_config.yaml* and */etc/aminer/template\_config.py*.

The basic structure of the logdata-anomaly-miner is illustrated in the folloging diagram:

.. image:: images/aminer-config-color.png
   :alt: Structure of the configuration-file: GENERAL, INPUT, PARSING, ANALYSING, EVENTHANDLING

-----------------
Analysis Pipeline
-----------------

The core component of the logdata-anomaly-miner is the "analysis pipeline". It consists of the parts INPUT, ANALYSIS and OUTPUT

.. image:: images/analysis-pipeline.png
   :alt: Parts of the analysis-pipeline

=======================
Configuration Reference
=======================

---------------------
General Configuration
---------------------

Supported settings:

LearnMode
~~~~~~~~~

* Type: boolean (True,False)
* Default: False

This options turns the LearnMode on globally.

.. warning:: This option can be overruled by the learn_mode that is configurable per analysis component.

.. code-block:: yaml

   LearnMode: True


AminerUser
~~~~~~~~~~

* Default: aminer

This option defines the system-user that owns the aminer-process.

.. code-block:: yaml

   AminerUser: 'aminer'

AminerGroup
~~~~~~~~~~~

* Default: aminer

This option defines the system-group that owns the aminer-process.

.. code-block:: yaml

   AminerGroup: 'aminer'

RemoteControlSocket
~~~~~~~~~~~~~~~~~~~

This option controls where the unix-domain-socket for the RemoteControl should be created. The socket will not be created if this option was not set.

.. code-block:: yaml

   RemoteControlSocket: '/var/lib/aminer/remcontrol.sock'

SuppressNewMatchPathDetector
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Default: False
* Type: boolean (True,False)

Disable the NewMatchPathDetector which detects new paths for logtypes.

.. code-block:: yaml

   SuppressNewMatchPathDetector: 'False'


LogResourceList
~~~~~~~~~~~~~~~

* Required: **True**
* Resource-Types: ``file://``, ``unix://``

Define the list of log resources to read from: the resources named here do not need to exist when aminer is started. This will just result in a warning. However if they exist, they have to be readable by the aminer process!

Supported types are:

* file://[path]: Read data from file, reopen it after rollover
* unix://[path]: Open the path as UNIX local socket for reading

.. code-block:: yaml

   LogResourceList:
       - 'file:///var/log/apache2/access.log' 
       - 'file:///home/ubuntu/data/mail.cup.com-train/daemon.log'
       - 'file:///home/ubuntu/data/mail.cup.com-train/auth.log'
       - 'file:///home/ubuntu/data/mail.cup.com-train/suricata/eve.json'
       - 'file:///home/ubuntu/data/mail.cup.com-train/suricata/fast.log'

Core.PersistenceDir
~~~~~~~~~~~~~~~~~~~

* Default: /var/lib/aminer

Read and store information to be used between multiple invocations of aminer in this directory. The directory must only be accessible to the 'AminerUser' but not group/world readable. On violation, aminer will refuse to start.

.. code-block:: yaml

   Core.PersistenceDir: '/var/lib/aminer'

Core.PersistencePeriod
~~~~~~~~~~~~~~~~~~~~~~

* Type: Number of seconds
* Default: 600

This options controls the logdata-anomaly-miner should write it's persistency to disk.

.. code-block:: yaml

   Core.PersistencePeriod: 600


Core.LogDir
~~~~~~~~~~~

* Default: /var/lib/aminer/log

Directory for logfiles. This directory must be writeable to the 'AminerUser'.

.. code-block:: yaml

   Core.LogDir: '/var/lib/aminer/log'

MailAlerting.TargetAddress
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Default: disabled

Define a target e-mail address to send alerts to. When undefined no e-mail notification hooks are added.

.. code-block:: yaml

   MailAlerting.TargetAddress: 'root@localhost'

MailAlerting.FromAddress
~~~~~~~~~~~~~~~~~~~~~~~~

Sender address of e-mail alerts. When undefined, "sendmail" implementation on host will decide, which sender address should be used.

.. code-block:: yaml

   MailAlerting.FromAddress: 'root@localhost'

MailAlerting.SubjectPrefix
~~~~~~~~~~~~~~~~~~~~~~~~~~

* Default: "aminer Alerts"

Define, which text should be prepended to the standard aminer subject.

.. code-block:: yaml

   MailAlerting.SubjectPrefix: 'aminer Alerts:'

MailAlerting.AlertGraceTime
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Type: Number of seconds
* Default: 0 (any event can immediately trigger alerting)

Define a grace time after startup before aminer will react to an event and send the first alert e-mail.

.. code-block:: yaml

   MailAlerting.AlertGraceTime: 0

MailAlerting.EventCollectTime
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Type: Number of seconds
* Default: 10

Define how many seconds to wait after a first event triggered the alerting procedure before really sending out the e-mail. In that timespan, events are collected and will be sent all using a single e-mail.

.. code-block:: yaml

   MailAlerting.EventCollectTime: 10

MailAlerting.MinAlertGap
~~~~~~~~~~~~~~~~~~~~~~~~

* Type: Number of seconds
* Default: 600

Define the minimum time between two alert e-mails in seconds to avoid spamming. All events during this timespan are collected and sent out with the next report.

.. code-block:: yaml

   MailAlerting.MinAlertGap: 600

MailAlerting.MaxAlertGap
~~~~~~~~~~~~~~~~~~~~~~~~

* Type: Number of seconds
* Default: 600

Define the maximum time between two alert e-mails in seconds. When undefined this defaults to "MailAlerting.MinAlertGap". Otherwise this will activate an exponential backoff to reduce messages during permanent error states by increasing the alert gap by 50% when more alert-worthy events were recorded while the previous gap time was not yet elapsed.

.. code-block:: yaml

   MailAlerting.MaxAlertGap: 600

MailAlerting.MaxEventsPerMessage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Type: Number of events
* Default: 1000

Define how many events should be included in one alert mail at most.

.. code-block:: yaml

   MailAlerting.MaxEventsPerMessage: 1000

LogPrefix
~~~~~~~~~

This option defines the prefix for the output of each anomaly.

.. code-block:: yaml

   LogPrefix: ''

Log.StatisticsPeriod
~~~~~~~~~~~~~~~~~~~~

* Type: Number of seconds
* Default: 3600

Defines how often to write into stat-logfiles.

.. code-block:: yaml
   
   Log.StatisticsPeriod: 3600

Log.StatisticsLevel
~~~~~~~~~~~~~~~~~~~

* Type: Number of loglevel
* Default: 1

Defines the loglevel for the stat logs.

.. code-block:: yaml
   
   Log.StatisticsLevel: 2

Log.DebugLevel
~~~~~~~~~~~~~~

* Type: Number of loglevel
* Default: 1

Defines the loglevel of the aminer debug-logfile.

.. code-block:: yaml
   
   Log.DebugLevel: 2

Log.RemoteControlLogFile
~~~~~~~~~~~~~~~~~~~~~~~~

* Default: '/var/lib/aminer/log/aminerRemoteLog.txt'
* Type: string (path to the logfile)

Defines the path of the logfile for the RemoteControl.

.. code-block:: yaml

   Log.RemoteControlLogFile: '/var/log/aminerremotecontrol.log'

Log.StatisticsFile
~~~~~~~~~~~~~~~~~~

* Default: '/var/lib/aminer/log/statistics.log'
* Type: string (path to the logfile)

Defines the path of the stats-file.

.. code-block:: yaml

   Log.StatisticsFile: '/var/log/aminer-stats.log'

Log.DebugFile
~~~~~~~~~~~~~~~~~~

* Default: '/var/lib/aminer/log/aminer.log'
* Type: string (path to the logfile)

Defines the path of the debug-log-file.

.. code-block:: yaml

   Log.DebugFile: '/var/log/aminer.log'


-----
Input
-----

timestamp_paths
~~~~~~~~~~~~~~~

* Type: string or list of strings

Parser paths to DateTimeModelElements to set timestamp of log events.


.. code-block:: yaml

   timestamp_paths: '/model/time'

.. code-block:: yaml

   timestamp_paths: 
      - '/parser/model/time'
      - '/parser/model/type/execve/time'
      - '/parser/model/type/proctitle/time'
      - '/parser/model/type/syscall/time'
      - '/parser/model/type/path/time'

multi_source
~~~~~~~~~~~~

* Type: boolean (True,False)
* Default: False

Flag to enable chronologicly correct parsing from multiple input-logfiles.

.. code-block:: yaml

   multi_source: True

verbose
~~~~~~~

* Type: boolean (True,False)
* Default: False

Flag to enable that detailed information is shown for unparsed loglines.

.. code-block:: yaml

   verbose: True

eol_sep
~~~~~~~

* Default: '\n'

End of Line seperator for events. 

.. note:: Enables parsing of multiline logs.

.. code-block:: yaml

   eol_sep: '\r\n'

json_format
~~~~~~~~~~~

* Type: boolean (True,False)
* Default: False

Enables parsing of logs in json-format.

.. code-block:: yaml

   json_format: True


-------
Parsing
-------

There are some predefined standard-model-elements like *IpAddressDataModelElement*, *DateTimeModelElement*, *FixedDataModelElement* and so on. They are located in the python-source-tree of logdata-anomaly-miner. A comprehensive list of all possible standard-model-elements can be found below. Using these standard-model-elements it is possible to create custom parser models. Currently there are to methods of doing it:

1. Using a python-script that is located in */etc/aminer/conf-enabled*:

.. code-block:: python

   """ /etc/aminer/conf-enabled/ApacheAccessParsingModel.py"""
   from aminer.parsing.DateTimeModelElement import DateTimeModelElement
   from aminer.parsing.DecimalIntegerValueModelElement import DecimalIntegerValueModelElement
   from aminer.parsing.DelimitedDataModelElement import DelimitedDataModelElement
   from aminer.parsing.FirstMatchModelElement import FirstMatchModelElement
   from aminer.parsing.FixedDataModelElement import FixedDataModelElement
   from aminer.parsing.FixedWordlistDataModelElement import FixedWordlistDataModelElement
   from aminer.parsing.IpAddressDataModelElement import IpAddressDataModelElement
   from aminer.parsing.OptionalMatchModelElement import OptionalMatchModelElement
   from aminer.parsing.SequenceModelElement import SequenceModelElement
   from aminer.parsing.VariableByteDataModelElement import VariableByteDataModelElement
   
   def get_model():
       """Return a model to parse Apache Access logs from the AIT-LDS."""
       alphabet = b'!"#$%&\'()*+,-./0123456789:;<>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ\\^_`abcdefghijklmnopqrstuvwxyz{|}~=[]'
   
       model = SequenceModelElement('model', [
           FirstMatchModelElement('client_ip', [
               IpAddressDataModelElement('client_ip'),
               FixedDataModelElement('localhost', b'::1')
               ]),
           FixedDataModelElement('sp1', b' '),
           VariableByteDataModelElement('client_id', alphabet),
           FixedDataModelElement('sp2', b' '),
           VariableByteDataModelElement('user_id', alphabet),
           FixedDataModelElement('sp3', b' ['),
           DateTimeModelElement('time', b'%d/%b/%Y:%H:%M:%S'),
           FixedDataModelElement('sp4', b' +'),
           DecimalIntegerValueModelElement('tz'),
           FixedDataModelElement('sp5', b'] "'),
           FirstMatchModelElement('fm', [
               FixedDataModelElement('dash', b'-'),
               SequenceModelElement('request', [
                   FixedWordlistDataModelElement('method', [
                       b'GET', b'POST', b'PUT', b'HEAD', b'DELETE', b'CONNECT', b'OPTIONS', b'TRACE', b'PATCH']),
                   FixedDataModelElement('sp6', b' '),
                   DelimitedDataModelElement('request', b' ', b'\\'),
                   FixedDataModelElement('sp7', b' '),
                   DelimitedDataModelElement('version', b'"'),
                   ])
               ]),
           FixedDataModelElement('sp8', b'" '),
           DecimalIntegerValueModelElement('status_code'),
           FixedDataModelElement('sp9', b' '),
           DecimalIntegerValueModelElement('content_size'),
           OptionalMatchModelElement(
               'combined', SequenceModelElement('combined', [
                   FixedDataModelElement('sp10', b' "'),
                   DelimitedDataModelElement('referer', b'"', b'\\'),
                   FixedDataModelElement('sp11', b'" "'),
                   DelimitedDataModelElement('user_agent', b'"', b'\\'),
                   FixedDataModelElement('sp12', b'"'),
                   ])),
           ])
   
       return model

This parser can be used as "type" in **/etc/aminer/config.yml**:

.. code-block:: yaml

   Parser:
        - id: 'apacheModel'
          type: ApacheAccessModel
          name: 'apache'

.. warning:: Please do not create files with the ending "ModelElement" in /etc/aminer/conf-enabled!

2. Configuring the parser-model inline in **/etc/aminer/config.yml**

.. code-block:: yaml

   Parser:
           - id: host_name_model
             type: VariableByteDataModelElement
             name: 'host'
             args: '-.01234567890abcdefghijklmnopqrstuvwxyz:'
   
           - id: identity_model
             type: VariableByteDataModelElement
             name: 'ident'
             args: '-.01234567890abcdefghijklmnopqrstuvwxyz:'
   
           - id: user_name_model
             type: VariableByteDataModelElement
             name: 'user'
             args: '0123456789abcdefghijklmnopqrstuvwxyz.-'
   
           - id: new_time_model
             type: DateTimeModelElement
             name: 'time'
             args: '[%d/%b/%Y:%H:%M:%S +0000]'
   
           - id: sq3
             type: FixedDataModelElement
             name: 'sq3'
             args: ' "'
   
           - id: request_method_model
             type: FixedWordlistDataModelElement
             name: 'method'
             args:
                     - 'GET'
                     - 'POST'
                     - 'PUT'
                     - 'HEAD'
                     - 'DELETE'
                     - 'CONNECT'
                     - 'OPTIONS'
                     - 'TRACE'
                     - 'PATCH'
   
           - id: request_model
             type: VariableByteDataModelElement
             name: 'request'
             args: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-/()[]{}!$%&=<?*+'
   
           - id: http1
             type: FixedDataModelElement
             name: 'http1'
             args: ' HTTP/'
   
           - id: version_model
             type: VariableByteDataModelElement
             name: 'version'
             args: '0123456789.'
   
           - id: sq4
             type: FixedDataModelElement
             name: 'sq4'
             args: '" '
   
           - id: status_code_model
             type: DecimalIntegerValueModelElement
             name: 'status'
   
           - id: size_model
             type: DecimalIntegerValueModelElement
             name: 'size'
   
           - id: sq5
             type: FixedDataModelElement
             name: 'sq5'
             args: ' "-" "'
   
           - id: user_agent_model
             type: VariableByteDataModelElement
             name: 'useragent'
             args: '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-/()[]{}!$%&=<?*+;:_ '
   
           - id: sq6
             type: FixedDataModelElement
             name: 'sq6'
             args: '"'
   
           - id: 'startModel'
             start: True
             type: SequenceModelElement
             name: 'accesslog'
             args:
                     - host_name_model
                     - WHITESPACE
                     - identity_model
                     - WHITESPACE
                     - user_name_model
                     - WHITESPACE
                     - new_time_model
                     - sq3
                     - request_method_model
                     - WHITESPACE
                     - request_model
                     - http1
                     - version_model
                     - sq4
                     - status_code_model
                     - WHITESPACE
                     - size_model
                     - sq5
                     - user_agent_model
                     - sq6

The parsing section in **/etc/aminer/config.yml** starts with the statement "Parser:" followed by a list of parser-models. Every parser-model in this list must have a unique **id** and a **type**. The unique **id** can be used to cascade models by adding the **id** of an parser-model as arguments(**args**). One parser of this list must contain `start: True` that indicates the first parser-model:

.. code-block:: yaml

   Parser:
        - id: 'apacheModel'
          type: ApacheAccessModel
          name: 'apache'

        - id: 'startModel'
          start: True
          type: SequenceModelElement
          name: 'model'
          args: apacheModel

* **id**: must be a unique string
* **type**: must be an existing ModelElement
* **start**: a boolean value that indicates the starting model. Only one parser-model must have enabled this option!
* **args***: a string or a list of strings containing other parser-models. This option can be used to cascade different parser-models

.. note:: args can contain the constant WHITESPACE which is a preset for spaces


AnyByteDataModelElement
~~~~~~~~~~~~~~~~~~~~~~~

* **name**: string with the element-id

This parsing-element matches any byte but at least one. Thus a match will always span the complete data from beginning to end.

.. code-block:: yaml

   Parser:
        - id: 'anyModel'
          type: AnyByteDataModelElement
          name: 'anymodel'

Base64StringModelElement
~~~~~~~~~~~~~~~~~~~~~~~~

* **name**: string with the element-id

This parsing-element matches base64 strings.

.. code-block:: yaml

   Parser:
        - id: 'anyModel'
          type: Base64StringModelElement
          name: 'b64model'

DateTimeModelElement
~~~~~~~~~~~~~~~~~~~~

* **name**: string with the element-id


This element parses dates using a custom, timezone and locale-aware implementation similar to strptime.

.. code-block:: yaml

   Parser:
        - id: 'anyModel'
          type: Base64StringModelElement
          name: 'b64model'


---------
Analysing
---------

-------------
EventHandling
-------------
