# skipcq: FLK-D208
"""package not used.
import unittest
from aminer.generic import CronParsingModel
from aminer.parsing.MatchContext import MatchContext
from unit.TestBase import TestBase

'''
These testcases are testing the CronParsingModel with the Basis Path Testing method. The Modified Condition / Decisision
Coverage is also accomplished, because the conditions are all simple, which means it is tested if the path is reached.
The used paths can be seen in the provided flowchart.
The child elements of the CronParsingModel could be tested, but they are assumed to be working as intended,
because there should be individual test cases for every parser model.
'''
class CronParsingModelTest(TestBase):

    '''
    1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8
    '''
    def test1(self):
      self.matchContext = MatchContext(b'CRON[25537]: (root) CMD ping 8.8.8.8')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(b'CRON[25537]: (root) CMD ping 8.8.8.8',
        self.cronParsingModel.getMatchElement('stdExec', self.matchContext).getMatchString())

    '''
    1 -> 18 -> 33
    '''
    def test2(self):
      self.matchContext = MatchContext(b'systemd[1]: Started Daily apt download activities.')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('stdExec', self.matchContext))

    '''
    1 -> 2 -> 19 -> 33
    '''
    def test3(self):
      self.matchContext = MatchContext(b'CRON[ 25537 ]: (root) CMD ping 8.8.8.8')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('stdExec', self.matchContext))

    '''
    1 -> 2 -> 3 -> 20 -> 33
    '''
    def test4(self):
      self.matchContext = MatchContext(b'CRON[25537]:(root) CMD ping 8.8.8.8')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('stdExec', self.matchContext))

    '''
    1 -> 2 -> 3 -> 4 -> 9 -> 13 -> 14 -> 15 -> 16 -> 17
    '''
    def test5(self):
      self.matchContext = MatchContext(b'CRON[25537]: pam_unix(cron:session): session opened for user root by (uid=0)')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(b'CRON[25537]: pam_unix(cron:session): session opened for user root by (uid=0)',
        self.cronParsingModel.getMatchElement('stdPam', self.matchContext).getMatchString())

      self.matchContext = MatchContext(b'CRON[25537]: pam_unix(cron:session): session closed for user root')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(b'CRON[25537]: pam_unix(cron:session): session closed for user root',
        self.cronParsingModel.getMatchElement('stdPam', self.matchContext).getMatchString())

    '''
    1 -> 2 -> 3 -> 4 -> 9 -> 21 -> 33
    '''
    def test6(self):
      self.matchContext = MatchContext(b'CRON[25537]: CRON info (No MTA installed, discarding output)')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('stdPam', self.matchContext))

    '''
    1 -> 2 -> 3 -> 4 -> 5 -> 10 -> 21 -> 33
    '''
    def test7(self):
      self.matchContext = MatchContext(b'CRON[25537]: (CRON;) info (No MTA installed, discarding output)')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('stdPam', self.matchContext))

    '''
    1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 11 -> 21 -> 33
    '''
    def test8(self):
      self.matchContext = MatchContext(b'CRON[25537]: (CRON) info (No MTA installed, discarding output)')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('stdPam', self.matchContext))

    '''
    1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 12 -> 21 -> 33
    '''
    def test9(self):
      self.matchContext = MatchContext(b'CRON[25537]: (root) CMD ')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('stdPam', self.matchContext))

    '''
    1 -> 2 -> 3 -> 4 -> 9 -> 13 -> 22 -> 33
    '''
    def test10(self):
      self.matchContext = MatchContext(b'CRON[25537]: pam_unix(cron:session): session changed for user root by (uid=0)')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('stdPam', self.matchContext))

    '''
    1 -> 2 -> 3 -> 4 -> 9 -> 13 -> 14 -> 23 -> 33
    '''
    def test11(self):
      self.matchContext = MatchContext(b'CRON[25537]: pam_unix(cron:session): session opened for root')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('stdPam', self.matchContext))

    '''
    1 -> 2 -> 3 -> 4 -> 9 -> 13 -> 14 -> 15 -> 24 -> 33
    '''
    def test12(self):
      self.matchContext = MatchContext(b'CRON[25537]: pam_unix(cron:session): session opened for user /usr/root')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('stdPam', self.matchContext))

    '''
    1 -> 2 -> 3 -> 4 -> 9 -> 13 -> 14 -> 15 -> 16 -> 25 -> 33
    Should this case return a MatchElement? It could be an anomaly if a session is opened by another user than root.
    '''
    def test13(self):
      self.matchContext = MatchContext(b'CRON[25537]: pam_unix(cron:session): session opened for user user by (uid=2)')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('stdPam', self.matchContext))

    '''
    1 -> 18 -> 26 -> 27 -> 28 -> 29 -> 30 -> 31 -> 32
    '''
    def test14(self):
      self.matchContext = MatchContext(b'cron[25537]: (*system*mailman) RELOAD (/var/spool/cron/mailman)')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(b'cron[25537]: (*system*mailman) RELOAD (/var/spool/cron/mailman)',
        self.cronParsingModel.getMatchElement('low', self.matchContext).getMatchString())

    '''
    1 -> 18 -> 26 -> 34
    '''
    def test15(self):
      self.matchContext = MatchContext(b'cron[ 25537 ]: (*system*mailman) RELOAD (/var/spool/cron/mailman)')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('low', self.matchContext))

    '''
    1 -> 18 -> 26 -> 27 -> 35
    '''
    def test16(self):
      self.matchContext = MatchContext(b'cron[25537]:(*system*mailman) RELOAD (/var/spool/cron/mailman)')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('low', self.matchContext))

    '''
    1 -> 18 -> 26 -> 27 -> 28 -> 36
    The DelimitedDataModelElement should only return a MatchElement if at least one byte is between the start and
    the delimeter.
    '''
    def test17(self):
      self.matchContext = MatchContext(b'cron[25537]: (*system*) RELOAD (/var/spool/cron/mailman)')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('low', self.matchContext))

    '''
    1 -> 18 -> 26 -> 27 -> 28 -> 29 -> 37
    '''
    def test18(self):
      self.matchContext = MatchContext(b'cron[25537]: (*system*) RELOAD /var/spool/cron/mailman')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('low', self.matchContext))

    '''
    1 -> 18 -> 26 -> 27 -> 28 -> 29 -> 30 -> 38
    '''
    def test19(self):
      self.matchContext = MatchContext(b'cron[25537]: (*system*) RELOAD ()')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('low', self.matchContext))

    '''
    1 -> 18 -> 26 -> 27 -> 28 -> 29 -> 30 -> 31 -> 39
    '''
    def test20(self):
      self.matchContext = MatchContext(b'cron[25537]: (*system*) RELOAD (/var/spool/cron/mailman')
      self.cronParsingModel = CronParsingModel.getModel()
      self.assertEqual(None, self.cronParsingModel.getMatchElement('low', self.matchContext))


if __name__ == "__main__":
    unittest.main()
    """
