import time

from aminer.analysis.NewMatchIdValueComboDetector import NewMatchIdValueComboDetector
from aminer.input.LogAtom import LogAtom
from aminer.parsing import FirstMatchModelElement, SequenceModelElement, FixedDataModelElement, DelimitedDataModelElement, \
    DecimalIntegerValueModelElement, FixedWordlistDataModelElement, AnyByteDataModelElement, MatchContext, ParserMatch
from unit.TestBase import TestBase


class NewMatchIdValueComboDetectorTest(TestBase):
    """Unittests for the NewMatchIdValueComboDetector."""

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

    expected_allowlist_string = "Allowlisted path(es) parser/type/path/name, parser/type/syscall/syscall with %s."

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

    def test1receive_match_in_time_with_auto_include_flag(self):
        """This test case checks if log_atoms are accepted as expected with the auto_include_flag=True."""
        description = 'test1newMatchIdValueComboDetectorTest'
        output_stream_empty_results = [True, False, True, False, True, False, True, True, True, True, True, True, True, True, False, False,
                                       False, True, False, True, False]
        id_dict_current_results = [
            {1: {'parser/type/syscall/syscall': 1}}, {}, {2: {'parser/type/syscall/syscall': 2}}, {},
            {3: {'parser/type/syscall/syscall': 3}}, {}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 4: {'parser/type/syscall/syscall': 1}}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 5: {'parser/type/path/name': 'two'}}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 6: {'parser/type/syscall/syscall': 4}},
            {100: {'parser/type/syscall/syscall': 1}, 6: {'parser/type/syscall/syscall': 4}, 7: {'parser/type/path/name': 'five'}},
            {100: {'parser/type/syscall/syscall': 1}, 6: {'parser/type/syscall/syscall': 4}, 7: {'parser/type/path/name': 'five'},
                8: {'parser/type/syscall/syscall': 6}},
            {100: {'parser/type/syscall/syscall': 1}, 7: {'parser/type/path/name': 'five'}, 8: {'parser/type/syscall/syscall': 6}},
            {100: {'parser/type/syscall/syscall': 1}, 8: {'parser/type/syscall/syscall': 6}}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 9: {'parser/type/syscall/syscall': 2}}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 10: {'parser/type/path/name': 'one'}}, {100: {'parser/type/syscall/syscall': 1}}]
        id_dict_old_results = [{}] * 21
        min_allowed_time_diff = 0.1
        log_atoms = []
        for line in self.log_lines:
            t = time.time()
            log_atoms.append(
                LogAtom(line, ParserMatch(self.parsing_model.get_match_element('parser', MatchContext(line))), t, self.__class__.__name__))
        new_match_id_value_combo_detector = NewMatchIdValueComboDetector(self.aminer_config, [
            'parser/type/path/name', 'parser/type/syscall/syscall'], [self.stream_printer_event_handler],
            id_path_list=['parser/type/path/id', 'parser/type/syscall/id'], min_allowed_time_diff=min_allowed_time_diff,
            auto_include_flag=True, allow_missing_values_flag=True, persistence_id='audit_type_path', output_log_line=False)
        self.analysis_context.register_component(new_match_id_value_combo_detector, description)

        for i, log_atom in enumerate(log_atoms):
            self.assertTrue(new_match_id_value_combo_detector.receive_atom(log_atom))
            self.assertEqual(self.output_stream.getvalue() == "", output_stream_empty_results[i], log_atom.raw_data)
            self.assertEqual(new_match_id_value_combo_detector.id_dict_current, id_dict_current_results[i])
            self.assertEqual(new_match_id_value_combo_detector.id_dict_old, id_dict_old_results[i])
            self.reset_output_stream()

    def test2receive_match_after_max_allowed_time_diff_with_auto_include_flag(self):
        """This test case checks if log_atoms are deleted after the maximal allowed time difference with the auto_include_flag=True."""
        description = 'test2newMatchIdValueComboDetectorTest'
        output_stream_empty_results = [True, False, True, False, True, False, True, True, True, True, True, True, True, True, False, False,
                                       False, True, False, True, False]
        id_dict_current_results = [
            {1: {'parser/type/syscall/syscall': 1}}, {}, {2: {'parser/type/syscall/syscall': 2}}, {},
            {3: {'parser/type/syscall/syscall': 3}}, {}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 4: {'parser/type/syscall/syscall': 1}}, {100: {'parser/type/syscall/syscall': 1}},
            {5: {'parser/type/path/name': 'two'}, 100: {'parser/type/syscall/syscall': 1}}, {}, {6: {'parser/type/syscall/syscall': 4}},
            {6: {'parser/type/syscall/syscall': 4}, 7: {'parser/type/path/name': 'five'}},
            {6: {'parser/type/syscall/syscall': 4}, 7: {'parser/type/path/name': 'five'}, 8: {'parser/type/syscall/syscall': 6}},
            {7: {'parser/type/path/name': 'five'}, 8: {'parser/type/syscall/syscall': 6}}, {}, {}, {9: {'parser/type/syscall/syscall': 2}},
            {}, {10: {'parser/type/path/name': 'one'}}, {}]
        id_dict_old_results = [{}] * 10 + [{100: {'parser/type/syscall/syscall': 1}}] * 5 + [{8: {'parser/type/syscall/syscall': 6}}] + [
            {}] * 5
        min_allowed_time_diff = 5
        log_atoms = []
        t = time.time()
        for line in self.log_lines:
            log_atoms.append(
                LogAtom(line, ParserMatch(self.parsing_model.get_match_element('parser', MatchContext(line))), t, self.__class__.__name__))
            t = t + min_allowed_time_diff * 0.25

        new_match_id_value_combo_detector = NewMatchIdValueComboDetector(self.aminer_config, [
            'parser/type/path/name', 'parser/type/syscall/syscall'], [self.stream_printer_event_handler],
            id_path_list=['parser/type/path/id', 'parser/type/syscall/id'], min_allowed_time_diff=min_allowed_time_diff,
            auto_include_flag=True, allow_missing_values_flag=True, persistence_id='audit_type_path', output_log_line=False)
        self.analysis_context.register_component(new_match_id_value_combo_detector, description)

        for i, log_atom in enumerate(log_atoms):
            self.assertTrue(new_match_id_value_combo_detector.receive_atom(log_atom))
            self.assertEqual(self.output_stream.getvalue() == "", output_stream_empty_results[i], log_atom.raw_data)
            self.assertEqual(new_match_id_value_combo_detector.id_dict_current, id_dict_current_results[i], log_atom.raw_data)
            self.assertEqual(new_match_id_value_combo_detector.id_dict_old, id_dict_old_results[i])
            self.reset_output_stream()

    def test3receive_match_in_time_without_auto_include_flag(self):
        """This test case checks if log_atoms are accepted as expected with the auto_include_flag=False."""
        description = 'test3newMatchIdValueComboDetectorTest'
        output_stream_empty_results = [True, False, True, False, True, False, True, True, False, True, False, True, True, True, False,
                                       False, False, True, False, True, False]
        id_dict_current_results = [
            {1: {'parser/type/syscall/syscall': 1}}, {}, {2: {'parser/type/syscall/syscall': 2}}, {},
            {3: {'parser/type/syscall/syscall': 3}}, {}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 4: {'parser/type/syscall/syscall': 1}}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 5: {'parser/type/path/name': 'two'}}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 6: {'parser/type/syscall/syscall': 4}},
            {100: {'parser/type/syscall/syscall': 1}, 6: {'parser/type/syscall/syscall': 4}, 7: {'parser/type/path/name': 'five'}},
            {100: {'parser/type/syscall/syscall': 1}, 6: {'parser/type/syscall/syscall': 4}, 7: {'parser/type/path/name': 'five'},
                8: {'parser/type/syscall/syscall': 6}},
            {100: {'parser/type/syscall/syscall': 1}, 7: {'parser/type/path/name': 'five'}, 8: {'parser/type/syscall/syscall': 6}},
            {100: {'parser/type/syscall/syscall': 1}, 8: {'parser/type/syscall/syscall': 6}}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 9: {'parser/type/syscall/syscall': 2}}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 10: {'parser/type/path/name': 'one'}}, {100: {'parser/type/syscall/syscall': 1}}]
        id_dict_old_results = [{}] * 21
        min_allowed_time_diff = 0.1
        log_atoms = []
        for line in self.log_lines:
            t = time.time()
            log_atoms.append(
                LogAtom(line, ParserMatch(self.parsing_model.get_match_element('parser', MatchContext(line))), t, self.__class__.__name__))
        new_match_id_value_combo_detector = NewMatchIdValueComboDetector(self.aminer_config, [
            'parser/type/path/name', 'parser/type/syscall/syscall'], [self.stream_printer_event_handler],
            id_path_list=['parser/type/path/id', 'parser/type/syscall/id'], min_allowed_time_diff=min_allowed_time_diff,
            auto_include_flag=False, allow_missing_values_flag=True, persistence_id='audit_type_path', output_log_line=False)
        self.analysis_context.register_component(new_match_id_value_combo_detector, description)

        for i, log_atom in enumerate(log_atoms):
            self.assertTrue(new_match_id_value_combo_detector.receive_atom(log_atom))
            self.assertEqual(self.output_stream.getvalue() == "", output_stream_empty_results[i], log_atom.raw_data)
            self.assertEqual(new_match_id_value_combo_detector.id_dict_current, id_dict_current_results[i])
            self.assertEqual(new_match_id_value_combo_detector.id_dict_old, id_dict_old_results[i])
            self.assertEqual(new_match_id_value_combo_detector.known_values, [])
            self.reset_output_stream()

    def test4receive_match_after_max_allowed_time_diff_without_auto_include_flag(self):
        """This test case checks if log_atoms are deleted after the maximal allowed time difference with the auto_include_flag=False."""
        description = 'test4newMatchIdValueComboDetectorTest'
        output_stream_empty_results = [True, False, True, False, True, False, True, True, False, True, False, True, True, True, False,
                                       False, False, True, False, True, False]
        id_dict_current_results = [
            {1: {'parser/type/syscall/syscall': 1}}, {}, {2: {'parser/type/syscall/syscall': 2}}, {},
            {3: {'parser/type/syscall/syscall': 3}}, {}, {100: {'parser/type/syscall/syscall': 1}},
            {100: {'parser/type/syscall/syscall': 1}, 4: {'parser/type/syscall/syscall': 1}}, {100: {'parser/type/syscall/syscall': 1}},
            {5: {'parser/type/path/name': 'two'}, 100: {'parser/type/syscall/syscall': 1}}, {}, {6: {'parser/type/syscall/syscall': 4}},
            {6: {'parser/type/syscall/syscall': 4}, 7: {'parser/type/path/name': 'five'}},
            {6: {'parser/type/syscall/syscall': 4}, 7: {'parser/type/path/name': 'five'}, 8: {'parser/type/syscall/syscall': 6}},
            {7: {'parser/type/path/name': 'five'}, 8: {'parser/type/syscall/syscall': 6}}, {}, {}, {9: {'parser/type/syscall/syscall': 2}},
            {}, {10: {'parser/type/path/name': 'one'}}, {}]
        id_dict_old_results = [{}] * 10 + [{100: {'parser/type/syscall/syscall': 1}}] * 5 + [{8: {'parser/type/syscall/syscall': 6}}] + [
            {}] * 5
        min_allowed_time_diff = 5
        log_atoms = []
        t = time.time()
        for line in self.log_lines:
            log_atoms.append(
                LogAtom(line, ParserMatch(self.parsing_model.get_match_element('parser', MatchContext(line))), t, self.__class__.__name__))
            t = t + min_allowed_time_diff * 0.25

        new_match_id_value_combo_detector = NewMatchIdValueComboDetector(self.aminer_config, [
            'parser/type/path/name', 'parser/type/syscall/syscall'], [self.stream_printer_event_handler],
            id_path_list=['parser/type/path/id', 'parser/type/syscall/id'], min_allowed_time_diff=min_allowed_time_diff,
            auto_include_flag=False, allow_missing_values_flag=True, persistence_id='audit_type_path', output_log_line=False)
        self.analysis_context.register_component(new_match_id_value_combo_detector, description)

        for i, log_atom in enumerate(log_atoms):
            self.assertTrue(new_match_id_value_combo_detector.receive_atom(log_atom))
            self.assertEqual(self.output_stream.getvalue() == "", output_stream_empty_results[i], log_atom.raw_data)
            self.assertEqual(new_match_id_value_combo_detector.id_dict_current, id_dict_current_results[i], log_atom.raw_data)
            self.assertEqual(new_match_id_value_combo_detector.id_dict_old, id_dict_old_results[i])
            self.assertEqual(new_match_id_value_combo_detector.known_values, [])
            self.reset_output_stream()

    def test5allowlist_unknown_target_path(self):
        """This test case checks if a unknown target path can be added to the known_values with the allowlist_event method."""
        description = 'test5newMatchIdValueComboDetectorTest'
        min_allowed_time_diff = 5
        new_match_id_value_combo_detector = NewMatchIdValueComboDetector(self.aminer_config, [
            'parser/type/path/name', 'parser/type/syscall/syscall'], [self.stream_printer_event_handler],
            id_path_list=['parser/type/path/id', 'parser/type/syscall/id'], min_allowed_time_diff=min_allowed_time_diff,
            auto_include_flag=False, allow_missing_values_flag=True, persistence_id='audit_type_path', output_log_line=False)
        self.analysis_context.register_component(new_match_id_value_combo_detector, description)
        self.assertEqual(new_match_id_value_combo_detector.known_values, [])
        event_data = {'parser/type/syscall/syscall': 1, 'parser/type/path/name': 'one'}
        output = new_match_id_value_combo_detector.allowlist_event(
            'Analysis.%s' % new_match_id_value_combo_detector.__class__.__name__, event_data, None)
        self.assertEqual(new_match_id_value_combo_detector.known_values, [
            {'parser/type/syscall/syscall': 1, 'parser/type/path/name': 'one'}])
        self.assertEqual(output, self.expected_allowlist_string % event_data)

        event_data = {'parser/type/syscall/syscall': 2, 'parser/type/path/name': 'two'}
        output = new_match_id_value_combo_detector.allowlist_event(
            'Analysis.%s' % new_match_id_value_combo_detector.__class__.__name__, event_data, None)
        self.assertEqual(new_match_id_value_combo_detector.known_values, [
            {'parser/type/syscall/syscall': 1, 'parser/type/path/name': 'one'},
            {'parser/type/syscall/syscall': 2, 'parser/type/path/name': 'two'}])
        self.assertEqual(output, self.expected_allowlist_string % event_data)

    def test6allowlist_known_target_path(self):
        """This test case checks if a known target path is not added twice to the known_values with the allowlist_event method."""
        description = 'test6newMatchIdValueComboDetectorTest'
        min_allowed_time_diff = 5
        new_match_id_value_combo_detector = NewMatchIdValueComboDetector(self.aminer_config, [
            'parser/type/path/name', 'parser/type/syscall/syscall'], [self.stream_printer_event_handler],
            id_path_list=['parser/type/path/id', 'parser/type/syscall/id'], min_allowed_time_diff=min_allowed_time_diff,
            auto_include_flag=False, allow_missing_values_flag=True, persistence_id='audit_type_path', output_log_line=False)
        self.analysis_context.register_component(new_match_id_value_combo_detector, description)
        self.assertEqual(new_match_id_value_combo_detector.known_values, [])
        event_data = {'parser/type/syscall/syscall': 1, 'parser/type/path/name': 'one'}
        output = new_match_id_value_combo_detector.allowlist_event(
            'Analysis.%s' % new_match_id_value_combo_detector.__class__.__name__, event_data, None)
        self.assertEqual(new_match_id_value_combo_detector.known_values,
                         [{'parser/type/syscall/syscall': 1, 'parser/type/path/name': 'one'}])
        self.assertEqual(output, self.expected_allowlist_string % event_data)

        event_data = {'parser/type/syscall/syscall': 1, 'parser/type/path/name': 'one'}
        output = new_match_id_value_combo_detector.allowlist_event(
            'Analysis.%s' % new_match_id_value_combo_detector.__class__.__name__, event_data, None)
        self.assertEqual(new_match_id_value_combo_detector.known_values,
                         [{'parser/type/syscall/syscall': 1, 'parser/type/path/name': 'one'}])
        self.assertEqual(output, self.expected_allowlist_string % event_data)
