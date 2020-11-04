import time
import unittest
from aminer.analysis.EventTypeDetector import EventTypeDetector
from aminer.input import LogAtom
from aminer.parsing import FirstMatchModelElement, SequenceModelElement, FixedDataModelElement, DelimitedDataModelElement, \
    DecimalIntegerValueModelElement, FixedWordlistDataModelElement, AnyByteDataModelElement, ParserMatch, MatchContext, MatchElement
from unit.TestBase import TestBase


class EventTypeDetectorTest(TestBase):
    """Unittests for the EventTypeDetector."""

    log_lines = [
        b'type=SYSCALL msg=audit(1580367384.000:1): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 '
        b'ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 '
        b'comm="apache2" exe="/usr/sbin/apache2" key=(null)',
        b'type=PATH msg=audit(1580367385.000:1): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
        b'nametype=NORMAL',
        b'type=SYSCALL msg=audit(1580367386.000:2): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 '
        b'ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 '
        b'comm="apache2" exe="/usr/sbin/apache2" key=(null)',
        b'type=PATH msg=audit(1580367387.000:2): item=0 name="two" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
        b'nametype=NORMAL',
        b'type=SYSCALL msg=audit(1580367388.000:3): arch=c000003e syscall=3 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 '
        b'ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 '
        b'comm="apache2" exe="/usr/sbin/apache2" key=(null)',
        b'type=PATH msg=audit(1580367389.000:3): item=0 name="three" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
        b'nametype=NORMAL',
        b'type=SYSCALL msg=audit(1580367388.500:100): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1'
        b' ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 '
        b'comm="apache2" exe="/usr/sbin/apache2" key=(null)',
        b'type=SYSCALL msg=audit(1580367390.000:4): arch=c000003e syscall=1 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 '
        b'ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 '
        b'comm="apache2" exe="/usr/sbin/apache2" key=(null)',
        b'type=PATH msg=audit(1580367391.000:4): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
        b'nametype=NORMAL',
        b'type=PATH msg=audit(1580367392.000:5): item=0 name="two" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
        b'nametype=NORMAL',
        b'type=SYSCALL msg=audit(1580367393.000:5): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 '
        b'ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 '
        b'comm="apache2" exe="/usr/sbin/apache2" key=(null)',
        b'type=SYSCALL msg=audit(1580367394.000:6): arch=c000003e syscall=4 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 '
        b'ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 '
        b'comm="apache2" exe="/usr/sbin/apache2" key=(null)',
        b'type=PATH msg=audit(1580367395.000:7): item=0 name="five" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
        b'nametype=NORMAL',
        b'type=SYSCALL msg=audit(1580367396.000:8): arch=c000003e syscall=6 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 '
        b'ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 '
        b'comm="apache2" exe="/usr/sbin/apache2" key=(null)',
        b'type=PATH msg=audit(1580367397.000:6): item=0 name="four" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
        b'nametype=NORMAL',
        b'type=SYSCALL msg=audit(1580367398.000:7): arch=c000003e syscall=5 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 '
        b'ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 '
        b'comm="apache2" exe="/usr/sbin/apache2" key=(null)',
        b'type=PATH msg=audit(1580367399.000:8): item=0 name="six" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
        b'nametype=NORMAL',
        b'type=SYSCALL msg=audit(1580367400.000:9): arch=c000003e syscall=2 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 '
        b'ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 '
        b'comm="apache2" exe="/usr/sbin/apache2" key=(null)',
        b'type=PATH msg=audit(1580367401.000:9): item=0 name="three" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
        b'nametype=NORMAL',
        b'type=PATH msg=audit(1580367402.000:10): item=0 name="one" inode=790106 dev=fe:01 mode=0100666 ouid=1000 ogid=1000 rdev=00:00 '
        b'nametype=NORMAL',
        b'type=SYSCALL msg=audit(1580367403.000:10): arch=c000003e syscall=3 success=yes exit=21 a0=7ffda5863060 a1=0 a2=1b6 a3=4f items=1 '
        b'ppid=22913 pid=13187 auid=4294967295 uid=33 gid=33 euid=33 suid=33 fsuid=33 egid=33 sgid=33 fsgid=33 tty=(none) ses=4294967295 '
        b'comm="apache2" exe="/usr/sbin/apache2" key=(null)']

    parsing_model = FirstMatchModelElement('type', [SequenceModelElement('path', [
        FixedDataModelElement('type', b'type=PATH '), FixedDataModelElement('msg_audit', b'msg=audit('),
        DelimitedDataModelElement('msg', b':'), FixedDataModelElement('placeholder', b':'), DecimalIntegerValueModelElement('id'),
        FixedDataModelElement('item_string', b'): item='), DecimalIntegerValueModelElement('item'),
        FixedDataModelElement('name_string', b' name="'), DelimitedDataModelElement('name', b'"'),
        FixedDataModelElement('inode_string', b'" inode='), DecimalIntegerValueModelElement('inode'),
        FixedDataModelElement('dev_string', b' dev='), DelimitedDataModelElement('dev', b' '),
        FixedDataModelElement('mode_string', b' mode='), DecimalIntegerValueModelElement('mode'),
        FixedDataModelElement('ouid_string', b' ouid='), DecimalIntegerValueModelElement('ouid'),
        FixedDataModelElement('ogid_string', b' ogid='), DecimalIntegerValueModelElement('ogid'),
        FixedDataModelElement('rdev_string', b' rdev='), DelimitedDataModelElement('rdev', b' '),
        FixedDataModelElement('nametype_string', b' nametype='), FixedWordlistDataModelElement('nametype', [b'NORMAL', b'ERROR'])]),
        SequenceModelElement('syscall', [
            FixedDataModelElement('type', b'type=SYSCALL '), FixedDataModelElement('msg_audit', b'msg=audit('),
            DelimitedDataModelElement('msg', b':'), FixedDataModelElement('placeholder', b':'), DecimalIntegerValueModelElement('id'),
            FixedDataModelElement('arch_string', b'): arch='), DelimitedDataModelElement('arch', b' '),
            FixedDataModelElement('syscall_string', b' syscall='), DecimalIntegerValueModelElement('syscall'),
            FixedDataModelElement('success_string', b' success='), FixedWordlistDataModelElement('success', [b'yes', b'no']),
            FixedDataModelElement('exit_string', b' exit='), DecimalIntegerValueModelElement('exit'),
            AnyByteDataModelElement('remainding_data')])])

    def test1receive_atoms_with_default_values(self):
        """
        In this test case multiple log_atoms are received with default values of the EventTypeDetector.
        path_list is empty and all paths are learned dynamically in variable_key_list.
        """
        event_type_detector = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        log_atoms = []
        for line in self.log_lines:
            t = time.time()
            log_atoms.append(
                LogAtom(line, ParserMatch(self.parsing_model.get_match_element('parser', MatchContext(line))), t, self.__class__.__name__))
        for i, log_atom in enumerate(log_atoms):
            self.assertTrue(event_type_detector.receive_atom(log_atom))
            self.assertEqual(event_type_detector.total_records, i + 1)

    def test2receive_atoms_with_defined_path_list(self):
        """
        In this test case multiple log_atoms are received with default values of the EventTypeDetector.
        path_list is set to a static list of paths and variable_key_list should not be used.
        """
        event_type_detector = EventTypeDetector(
            self.aminer_config, [self.stream_printer_event_handler], path_list=['parser/type/path/nametype'])
        results = [True, False, True, False, True, False, True, True, False, False, True, True, False, True, False, True, False, True,
                   False, False, True]
        log_atoms = []
        for line in self.log_lines:
            t = time.time()
            log_atoms.append(
                LogAtom(line, ParserMatch(self.parsing_model.get_match_element('parser', MatchContext(line))), t, self.__class__.__name__))
        for i, log_atom in enumerate(log_atoms):
            old_vals = (event_type_detector.num_events, event_type_detector.num_eventlines,
                        event_type_detector.total_records, event_type_detector.longest_path)
            self.assertEqual(event_type_detector.receive_atom(log_atom), not results[i], i)
            if results[i]:
                self.assertEqual(old_vals, (
                    event_type_detector.num_events, event_type_detector.num_eventlines,
                    event_type_detector.total_records, event_type_detector.longest_path))

    def test3append_values_float(self):
        """This unittest checks the append_values method with raw_match_object being a float value."""
        event_type_detector = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        # initialize all values.
        t = time.time()
        log_atom = LogAtom(b'22.2', ParserMatch(MatchElement('path', '22.2', 22.2, None)), t, self.__class__.__name__)
        event_type_detector.receive_atom(log_atom)

        event_type_detector.values = [[[]]]
        event_type_detector.append_values(log_atom, 0)
        self.assertEqual(event_type_detector.values, [[[22.2]]])

        log_atom = LogAtom(b'22', ParserMatch(MatchElement('path', '22', 22, None)), t, self.__class__.__name__)
        event_type_detector.values = [[[]]]
        event_type_detector.append_values(log_atom, 0)
        self.assertEqual(event_type_detector.values, [[[22]]])

        log_atom = LogAtom(b'22.2', ParserMatch(MatchElement('path', '22', b'22', None)), t, self.__class__.__name__)
        event_type_detector.values = [[[]]]
        event_type_detector.append_values(log_atom, 0)
        self.assertEqual(event_type_detector.values, [[[22]]])

    def test4append_values_bytestring(self):
        """
        This unittest checks the append_values method with raw_match_object being a bytestring.
        This should trigger a ValueError and append the match_string.
        """
        event_type_detector = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        # initialize all values.
        t = time.time()
        log_atom = LogAtom(b'This is a string', ParserMatch(
            MatchElement('path', 'This is a string', b'This is a string', None)), t, self.__class__.__name__)
        event_type_detector.receive_atom(log_atom)

        event_type_detector.values = [[[]]]
        event_type_detector.append_values(log_atom, 0)
        self.assertEqual(event_type_detector.values, [[['This is a string']]])

        log_atom = LogAtom(b'24.05.', ParserMatch(MatchElement('path', '24.05.', b'24.05.', None)), t, self.__class__.__name__)
        event_type_detector.values = [[[]]]
        event_type_detector.append_values(log_atom, 0)
        self.assertEqual(event_type_detector.values, [[['24.05.']]])

    def test5check_value_reduction(self):
        """This unittest checks the functionality of reducing the values when the maxNumVals threshold is reached."""
        event_type_detector = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = time.time()
        val_list = [[[]]]
        for i in range(1, event_type_detector.max_num_vals + 1, 1):
            log_atom = LogAtom(str(i).encode(), ParserMatch(MatchElement('path', str(i), i, None)), t, self.__class__.__name__)
            val_list[0][0].append(float(i))
            self.assertTrue(event_type_detector.receive_atom(log_atom))
            self.assertEqual(event_type_detector.values, val_list)
        i += 1
        log_atom = LogAtom(str(i).encode(), ParserMatch(MatchElement('path', str(i), i, None)), t, self.__class__.__name__)
        val_list[0][0].append(float(i))
        self.assertTrue(event_type_detector.receive_atom(log_atom))
        self.assertEqual(event_type_detector.values, [[val_list[0][0][-event_type_detector.min_num_vals:]]])

    def test6persist_and_load_data(self):
        """This unittest checks the functionality of the persistence by persisting and reloading values."""
        event_type_detector = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        t = time.time()
        log_atom = LogAtom(b'22.2', ParserMatch(MatchElement('path', '22.2', 22.2, None)), t, self.__class__.__name__)
        event_type_detector.receive_atom(log_atom)
        event_type_detector.do_persist()
        event_type_detector_loaded = EventTypeDetector(self.aminer_config, [self.stream_printer_event_handler])
        self.assertEqual(event_type_detector.variable_key_list, event_type_detector_loaded.variable_key_list)
        self.assertEqual(event_type_detector.values, event_type_detector_loaded.values)
        self.assertEqual(event_type_detector.longest_path, event_type_detector_loaded.longest_path)
        self.assertEqual(event_type_detector.check_variables, event_type_detector_loaded.check_variables)
        self.assertEqual(event_type_detector.num_eventlines, event_type_detector_loaded.num_eventlines)


if __name__ == "__main__":
    unittest.main()
