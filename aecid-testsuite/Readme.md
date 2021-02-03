# aecid-testsuite

This project includes all kinds of tests for *AECID* and *aminer*. We used Docker instances for testing (see: [How to use the aecid-testsuite](https://github.com/ait-aecid/logdata-anomaly-miner/wiki/How-to-use-the-AECID-testsuite)).
The aminer was successfully tested with all tests in **Ubuntu 20.04** and **Debian Bullseye**.
In order to execute test classes the current path must be the *logdata-anomaly-miner* directory and the project structure must be as following:

## Unit-Tests

```logdata-anomaly-miner/
├── aminer
│    ├── __init__.py
│    ├── AminerConfig.py
│    ├── AnalysisChild.py
│    ├── analysis
│        ├── ...
│    ├── events
│        ├── ...
│    ├── generic
│        ├── ...
│    ├── input
│        ├── ...
│    ├── parsing
│        ├── ...
│    ├── input
│        ├── ...
│    ├── util
│        ├── ...
├── unit
     ├── __init__.py
     ├── analysis
          ├── __init__.py
          ├── AtomFiltersTest.py
          ├── EnhancedNewMatchPathValueComboDetectorTest.py
          ├── HistogramAnalysisTest.py
          ├── MatchValueAverageChangeDetectorTest.py
          ├── MatchValueStreamWriterTest.py
          ├── MissingMatchPathValueDetectorTest.py
          ├── NewMatchPathDetectorTest.py
          ├── NewMatchPathValueComboDetectorTest.py
          ├── NewMatchPathValueDetectorTest.py
          ├── RulesTest.py
          ├── TimestampCorrectionFiltersTest.py
          ├── TimestampsUnsortedDetectorTest.py
          ├── AllowlistViolationDetectorTest.py
          ├── ...
     ├── events
          ├── __init__.py
          ├── DefaultMailNotificationEventHandlerTest.py
          ├── StreamPrinterEventHandlerTest.py
          ├── SyslogWriterEventHandlerTest.py
          ├── UtilsTest.py
          ├── ...
     ├── generic
          ├── __init__.py
          ├── CronParsingModelTest.py
     ├── input
          ├── __init__.py
          ├── ByteStreamLineAtomizerTest.py
          ├── LogStreamTest.py
          ├── SimpleByteStreamLineAtomizerFactoryTest.py
          ├── SimpleMultisourceAtomSyncTest.py
          ├── SimpleUnparsedAtomHandlerTest.py
          ├── ...
     ├── testutilities
          ├── config.py
          ├── ...
     ├── parsing
          ├── __init__.py
          ├── AnyByteDataModelElementTest.py
          ├── DateTimeModelElementTest.py
          ├── DebugModelElementTest.py
          ├── DecimalFloatValueModelElementTest.py
          ├── DecimalIntegerValueModelElementTest.py
          ├── DelimitedDataModelElementTest.py
          ├── FirstMatchModelElementTest.py
          ├── FixedDataModelElementTest.py
          ├── FixedWordlistDataModelElementTest.py
          ├── HexStringModelElementTest.py
          ├── IpAddressDataModelElementTest.py
          ├── MatchElementTest.py
          ├── OptionalMatchModelElementTest.py
          ├── ParserMatchTest.py
          ├── RepeatedElementDataModelElementTest.py
          ├── SequenceModelElementTest.py
          ├── VariableByteDataModelElementTest.py
          ├── ...
     ├── util
          ├── __init__.py
          ├── JsonUtilTest.py
          ├── PersistenceUtilTest.py
          ├── SecureOSFunctionsTest.py
          ├── ...
```

Before starting any test case the path to the *config.py* should be changed. This can be achieved recursively by using following command (*/path/to/config.py* needs to be changed.):
```
sudo find . -type f -name "*Test.py" -print0 | xargs -0 sed -i -e 's#/home/user/Downloads/logdata-anomaly-miner-1.0.0/logdata-anomaly-miner/source/root/etc/aminer/config.py#/path/to/config.py#g'
```

Every test case can be executed by using following command in the main directory:
```
python3 -m unittest discover -s unit -p '*Test.py'
```

Single test classes can be executed with this command:
  ```
python3 -m unittest <path/to/test/class>
  ```
for example:
  ```
python3 -m unittest unit/parsing/AnyByteDataModelElementTest.py
  ```

The created mails under */var/spool/mail/root* should be deleted.

## Integration Testing:
To prepare every test the associated configuration file(s) first must be copied to */tmp*. The test-scripts **MUST NOT** be run as root. In addition, **declarations.sh** must be in the **same folder** as the integration test being run.

Please note that the script needs root privileges for running the *aminer* and all **persistent data is deleted** from */tmp/lib/aminer*!

### Integration Test 1:
In this integration test the learning phase of the aminer is tested. Multiple log-lines are used to be learned and checked. Some analysis components are used and all other lines are handled by the *SimpleUnparsedAtomHandler*. The Events are received by a *DefaultMailNotificationEventHandler* and a *StreamPrinterEventHandler*. Other lines are used to check if the pathes were learned and persisted in the persistence directory of the *aminer*. In this test case the *SubhandlerFilter* is suitable, because only one file, */tmp/syslog*, is monitored.

Following command makes the script executeable:
  ```
sudo chmod +x aminerIntegrationTest.sh
  ```

**config.py** must be copied to */tmp/config.py*. After all requirements have been met, the test can be run with the following command:
  ```
./aminerIntegrationTest.sh
  ```

### Integration Test 2:
In this integration test multiple log files are used with the *SimpleMultisourceAtomSync*-handler with (*config22.py*) and without (*config21.py*) a defaultTimestampPath. Therefor the test is divided into two parts. The log lines all have different times and are distributed in */tmp/syslog* and */tmp/auth.log* and should be in the correct order while running the test. Also the consistency and correctness of the output from the receiveEvent-method is tested. The *analysis*-components are same with the first integration test. This test case also uses the *SyslogWriterEventHandler* and checks the output with the expected results.

Following command makes the script executeable:
  ```
  sudo chmod +x aminerIntegrationTest2.sh
  ```

**config21.py** and **config22.py** must be copied to */tmp/*. After all requirements have been met, the test can be run with the following command:
  ```
./aminerIntegrationTest2.sh
  ```

## Demo:
The goal of this demo is to create a representative output of all the different *analysis*-components of the *aminer*. Every component has its own comment section, which starts with **:<<Comment** and ends with **Comment**. Just comment these two lines with an **'#'** to use the wished component.

Following command makes the script executeable:
  ```
sudo chmod +x aminerDemo.sh
  ```

**demo-config.py** must be copied to */tmp/demo-config.py*. After all requirements have been met, the test can be run with the following command:
  ```
./aminerDemo.sh
  ```

## Analysis Components Performance Testing:
The performance test is implemented as a single unittest class with multiple tests, each testing one analysis component. These tests throw logAtoms at different analysis components and counts how many actually can be processed in a predefined timeframe. There are three parts for each component based on the number of pathes/tuples/value pairs. This test uses the same config file as all other unittests. At the end of the test a summary of the results is printed.

The **waitingTime**-parameter should be changed, before running the test. The longer every test runs, the better and more precise results can be expected. A **waitingTime** of min. 10 seconds is recommended. The unittest must be copied next to the *aminer* folder.

The **iterations**-parameter defines how many times every single test will be run. This grants more precise results, as it excludes measuring errors. The result is displayed as an average, as well as with the respective values.

Following command starts the performance test:
  ```
python3 -m unittest AnalysisComponentsPerformanceTest.py
  ```

## System Performance Testing:
The goal of these performance tests is to simulate different scenarious of available computing power and memory. For this purpose a virtual machine is configured with more or less CPU's and RAM. 

The **first config (performance-config.py)** is very simple with very little output. It consists of following components:
#### Analysis
* NewMatchDetector
* NewMatchPathValueDetector

#### EventHandler
* StreamPrinterEventHandler

#### Parsing model:
* AnyByteDataModelElement

The **second config (performance-config1.py)** is very similar to the demo-config. It consists of following components:
#### Analysis
* SimpleMonotonicTimestampAdjust
* TimestampsUnsortedDetector
* AllowlistViolationDetector
		/model/Login Details/Past Time/Time/Minutes exists and
		/model/Login Details/Username != root
**or**

		/model/Login Details/Past Time/Time/Minutes does not exist and
		/model/Login Details exists
**or**

		/model/Login Details does not exist
* NewMatchDetector
* EnhancedNewMatchPathValueComboDetector 
		two attributes and output after 10000 data elements were collected
* HistogramAnalysis
		two different PathDependentHistogramAnalysis instances
* MatchValueAverageChangeDetector
* MatchValueStreamWriter
* NewMatchPathValueComboDetector
* NewMatchPathValueDetector
* MissingMatchPathValueDetector
* TimeCorrelationDetector
		output after 70k log lines
* TimeCorrelationViolationDetector

#### EventHandler
* StreamPrinterEventHandler

#### Parsing model:
* FirstMatchModelElement with 8 SequenceModelElements

The **third config (performance-config2.py)** is exactly the same as performance-config1.py, but it uses following EventHandlers. Due to the additional outputs the performance-config2 is much more resource hungry than performance-config1.

#### EventHandler
* StreamPrinterEventHandler
* SyslogWriterEventHandler
* DefaultMailNotificationEventHandler

For better comparison every test uses the same input logfile.

The results of these tests are a CSV file with measurements of the ressource usage of the system and the number of processed log lines in a predefined timeframe. For better documentation the name of the CSV file must contain the exact name of the computer, CPU and disk in the first line.

Before these tests can be run, it is necessary to copy the provided *AnalysisChild* and *ByteStreamLineAtomizer* classes into the *aminer* installation folder. These classes are adapted to contain a counter of every log line processed and are necessary to be able to evaluate the results.

The *aminer* requires a config file under */tmp/performance-config.py*. As there are multiple config files for every of the three tests, they must be renamed to *performance-config.py* in the */tmp* folder.

Following commands make the scripts executeable:
  ```
sudo chmod +x aminerSystemPerformanceTest.sh
sudo chmod +x multiplyLogFile.sh
  ```

With the *multiplyLogFile.sh* script it is possible to use one template file and copy it multiple times in the target file. Run the script as follows:
  ```
./multiplyLogFile.sh numberOfCopies templateFile targetFile
  ```

For example:
  ```
./multiplyLogFile.sh 270000 syslog-template /tmp/syslog
  ```

The *aminerSystemPerformanceTest.sh* script can be run as follows:
  ```
./aminerSystemPerformanceTest.sh runtime_in_seconds description
  ```

For example:
  ```
./aminerSystemPerformanceTest.sh 900 "Low performance test with many outputs. (./multiplyLogFile.sh 400000 syslog_low_performance_many_outputs-template /tmp/syslog)"
  ```

For comparison the minimal amount of log data for an 15 minute testing period on an Acer Aspire 5750g(8GB RAM, SSD) and an Ubuntu VM with 4GB RAM and 4 CPUs should be at least 3GB.

### Performance Test Results
#### Table Legend
| Word                                                                        | Key           |
|:-------------------------------------------------------:|:---------- -:|
| performance-config.py                                            | PC             |
| performance-config1.py                                          | PC1           |
| performance-config2.py                                          | PC2           |
| syslog_low_performance_many_outputs-template | syslog-LP  |
| syslog_high_performance-template                        | syslog-HP |

#### Acer Aspire 5750G / i7-2630QM Ubuntu VM
| Logfile | Config-File | Setup / Ressources | Total Time | Processed Log Lines | Processed Log Lines per Second | max. RAM usage in MB |
|:--------:|:------------:|:---------------------:|:------------:|:-----------------------:|:---------------------------------:|:-------------------:|
| syslog-LP | PC | 4GB / 4CPUs | 15 Minutes | 55.471.197 | 61.635 | - |
| syslog-LP | PC | 2GB / 2CPUs | 15 Minutes | 59.754.033 | 66.393 | - |
| syslog-LP | PC | 1GB / 1CPUs | 15 Minutes | 48.274.224 | 53.638 | - |
| syslog-LP | PC1 | 4GB / 4CPUs | 15 Minutes | 4.533.529 | 5.037 | - |
| syslog-LP | PC1 | 2GB / 2CPUs | 15 Minutes | 4.709.892 | 5.233 | - |
| syslog-LP | PC1 | 1GB / 1CPUs | 15 Minutes | 3.256.576 | 3.618 | - |
| syslog-LP | PC2 | 4GB / 4CPUs | 15 Minutes | 3.185.896 | 3.540 | - |
| syslog-LP | PC2 | 2GB / 2CPUs | 15 Minutes | 3.244.321 | 3.605 | - |
| syslog-LP | PC2 | 1GB / 1CPUs | 15 Minutes | 2.407.659 | 2.675 | - |
| syslog-HP | PC | 4GB / 4CPUs | 15 Minutes | 64.189.538 | 71.322 | - |
| syslog-HP | PC | 2GB / 2CPUs | 15 Minutes | 63.570.025 | 70.633 | - |
| syslog-HP | PC | 1GB / 1CPUs | 15 Minutes | 56.806.130 | 63.118 | - |
| syslog-HP | PC1 | 4GB / 4CPUs | 15 Minutes | 4.520.940 | 5.023 | - |
| syslog-HP | PC1 | 2GB / 2CPUs | 15 Minutes | 4.219.343 | 4.688 | - |
| syslog-HP | PC1 | 1GB / 1CPUs | 15 Minutes | 4.285.291 | 4.761 | - |
| syslog-HP | PC2 | 4GB / 4CPUs | 15 Minutes | 4.055.323 | 4.506 | - |
| syslog-HP | PC2 | 2GB / 2CPUs | 15 Minutes | 4.705.474 | 5.228 | - |
| syslog-HP | PC2 | 1GB / 1CPUs | 15 Minutes | 3.922.666 | 4.359 | - |


#### PC GTX 1060 - 16GB RAM / AMD FX-8350 Ubuntu VM
| Logfile | Config-File | Setup / Ressources | Total Time | Processed Log Lines | Processed Log Lines per Second | max. RAM usage in MB |
|:--------:|:------------:|:---------------------:|:------------:|:-----------------------:|:---------------------------------:|:-------------------:|
| syslog-LP | PC | 8GB / 6CPUs | 15 Minutes | 61.777.067 | 68.641 |          17          |
| syslog-LP | PC | 4GB / 4CPUs | 15 Minutes | 61.943.491 | 68.826 | 17 |
| syslog-LP | PC | 2GB / 2CPUs | 15 Minutes | 61.382.001 | 68.202 | 17 |
| syslog-LP | PC | 1GB / 1CPUs | 15 Minutes | 62.737.748 | 69.709 |          17          |
| syslog-LP | PC1 | 8GB / 6CPUs | 15 Minutes | 5.710.701 | 6.345 | 574 |
| syslog-LP | PC1 | 4GB / 4CPUs | 15 Minutes | 5.890.911 | 6.545 | 612 |
| syslog-LP | PC1 | 2GB / 2CPUs | 15 Minutes | 5.491.113 | 6.101 | 570 |
| syslog-LP | PC1 | 1GB / 1CPUs | 15 Minutes | 4.537.605 | 5.042 | 365 |
| syslog-LP | PC2 | 8GB / 6CPUs | 15 Minutes | 3.653.634 | 4.060 | 382 |
| syslog-LP | PC2 | 4GB / 4CPUs | 15 Minutes | 3.778.458 | 4.198 | 399 |
| syslog-LP | PC2 | 2GB / 2CPUs | 15 Minutes | 3.419.311 | 3.799 | 362 |
| syslog-LP | PC2 | 1GB / 1CPUs | 15 Minutes | 3.089.386 | 3.433 | 312 |
| syslog-HP | PC | 8GB / 6CPUs | 15 Minutes | 61.549.787 | 68.389 | 17 |
| syslog-HP | PC | 4GB / 4CPUs | 15 Minutes | 61.131.401 | 67.924 | 17 |
| syslog-HP | PC | 2GB / 2CPUs | 15 Minutes | 63.317.914 | 70.353 | 17 |
| syslog-HP | PC | 1GB / 1CPUs | 15 Minutes | 61.065.680 | 67.851 | 17 |
| syslog-HP | PC1 | 8GB / 6CPUs | 15 Minutes | 5.615.341 | 6.239 | 628 |
| syslog-HP | PC1 | 4GB / 4CPUs | 15 Minutes | 5.513.834 | 6.126 | 625 |
| syslog-HP | PC1 | 2GB / 2CPUs | 15 Minutes | 5.623.260 | 6.248 | 636 |
| syslog-HP | PC1 | 1GB / 1CPUs | 15 Minutes | 4.615.019 | 5.128 | 381 |
| syslog-HP | PC2 | 8GB / 6CPUs | 15 Minutes | 5.048.950 | 5.610 | 568 |
| syslog-HP | PC2 | 4GB / 4CPUs | 15 Minutes | 4.937.242 | 5.486 | 563 |
| syslog-HP | PC2 | 2GB / 2CPUs | 15 Minutes | 5.089.666 | 5.655 | 578 |
| syslog-HP | PC2 | 1GB / 1CPUs | 15 Minutes | 4.719.362 | 5.244 | 269 |

#### Acer Aspire 5750G / i7-2630QM Debian Server VM
| Logfile | Config-File | Setup / Ressources | Total Time | Processed Log Lines | Processed Log Lines per Second | max. RAM usage in MB |
|:--------:|:------------:|:---------------------:|:------------:|:-----------------------:|:---------------------------------:|:-------------------:|
| syslog-LP | PC | 512MB / 1CPU | 15 Minutes | 67.238.716 | 74.710 | 19 |
| syslog-LP | PC | 256MB / 1CPU | 15 Minutes | 61.126.602 | 67.918 | 21 |
| syslog-LP | PC1 | 512MB / 1CPU | 15 Minutes | 2.137.882 | 2.375 | 247 |
| syslog-LP | PC1 | 256MB / 1CPU | 15 Minutes | 2.528.231 | 2.809 | 134 |
| syslog-LP | PC2 | 512MB / 1CPU | 15 Minutes | 3.464.680 | 3.850 | 372 |
| syslog-LP | PC2 | 256MB / 1CPU | 15 Minutes | 400.981 | 446 | 60 |
| syslog-HP | PC | 512MB / 1CPU | 15 Minutes | 57.941.443 | 64.379 | 19 |
| syslog-HP | PC | 256MB / 1CPU | 15 Minutes | 48.065.223 | 53.406 | 21 |
| syslog-HP | PC1 | 512MB / 1CPU | 15 Minutes | 5.001.891 | 5.558 | - |
| syslog-HP | PC1 | 256MB / 1CPU | 15 Minutes | 3.412.159 | 3.791 | 124 |
| syslog-HP | PC2 | 512MB / 1CPU | 15 Minutes | 3.470.257 | 3.856 | 293 |
| syslog-HP | PC2 | 256MB / 1CPU | 15 Minutes | 2.690.593 | 2.990 | 108 |

#### Acer Aspire 5750G / i7-2630QM Ubuntu VM
| Logfile | Config-File | Setup / Ressources | Total Time | Processed Log Lines | Processed Log Lines per Second | max. RAM usage in MB |
|:--------:|:------------:|:---------------------:|:------------:|:-----------------------:|:---------------------------------:|:-------------------:|
| syslog-LP | PC | 128MB / 1CPU | 15 Minutes | 49.101.720 | 54.557 | 17 |
| syslog-LP | PC | 128MB / 0.5CPU | 15 Minutes | 32.363.865 | 35.960 | 17 |
| syslog-LP | PC | 64MB / 0.3CPU | 15 Minutes | 21.608.727 | 24.010 | 17 |
| syslog-LP | PC | 32MB / 0.1CPU | 15 Minutes | 8.074.814 | 8.972 | 17 |
| syslog-LP | PC1 | 128MB / 1CPU | 15 Minutes | 3.584.950 | 3.983 | 27 |
| syslog-LP | PC1 | 128MB / 0.5CPU | 15 Minutes | 1.947.903 | 2.164 | 23 |
| syslog-LP | PC1 | 64MB / 0.3CPU | 15 Minutes | 1.514.218 | 1.682 | 23 |
| syslog-LP | PC1 | 32MB / 0.1CPU | 15 Minutes | 607.432 | 675 | 19 |
| syslog-LP | PC2 | 128MB / 1CPU | 15 Minutes | 3.254.866 | 3.617 | 29 |
| syslog-LP | PC2 | 128MB / 0.5CPU | 15 Minutes | 2.116.148 | 2.351 | 25 |
| syslog-LP | PC2 | 64MB / 0.3CPU | 15 Minutes | 1.387.813 | 1.542 | 23 |
| syslog-LP | PC2 | 32MB / 0.1CPU | 15 Minutes | 454.343 | 505 | 20 |
| syslog-HP | PC | 128MB / 1CPU | 15 Minutes | 47.438.773 | 52.710 | 17 |
| syslog-HP | PC | 128MB / 0.5CPU | 15 Minutes | 27.866.705 | 30.963 | 17 |
| syslog-HP | PC | 64MB / 0.3CPU | 15 Minutes | 21.135.759 | 23.484 | 17 |
| syslog-HP | PC | 32MB / 0.1CPU | 15 Minutes | 7.599.078 | 8.443 | 17 |
| syslog-HP | PC1 | 128MB / 1CPU | 15 Minutes | 3.919.038 | 4.354 | 32 |
| syslog-HP | PC1 | 128MB / 0.5CPU | 15 Minutes | 2.245.924 | 2.495 | 27 |
| syslog-HP | PC1 | 64MB / 0.3CPU | 15 Minutes | 1.634.930 | 1.817 | 23 |
| syslog-HP | PC1 | 32MB / 0.1CPU | 15 Minutes | 586.596 | 652 | 20 |
| syslog-HP | PC2 | 128MB / 1CPU | 15 Minutes | 3.046.036 | 3.384 | 30 |
| syslog-HP | PC2 | 128MB / 0.5CPU | 15 Minutes | 2.192.141 | 2.436 | 27 |
| syslog-HP | PC2 | 64MB / 0.3CPU | 15 Minutes | 1.441.671 | 1.602 | 24 |
| syslog-HP | PC2 | 32MB / 0.1CPU | 15 Minutes | 563.011 | 626 | 20 |
