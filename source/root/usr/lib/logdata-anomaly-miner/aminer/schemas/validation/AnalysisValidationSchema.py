# skipcq: PYL-W0104
{
    'Analysis': {
        'required': False,
        'type': 'list',
        'nullable': True,
        'schema': {
            'type': 'dict',
            'allow_unknown': False,
            'oneof_schema': [
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['AllowlistViolationDetector'], 'required': True},
                    'allowlist_rules': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MatchPathFilter'], 'required': True},
                    'parsed_atom_handler_lookup_list': {
                        'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'string', 'nullable': True}}, 'required': True},
                    'default_parsed_atom_handler': {'type': 'string', 'nullable': True},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MatchValueFilter'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'parsed_atom_handler_dict': {
                        'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': 'string'}}, 'required': True},
                    'default_parsed_atom_handler': {'type': 'string', 'nullable': True},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['EnhancedNewMatchPathValueComboDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'allow_missing_values': {'type': 'boolean', 'required': False, 'default': False},
                    'learn_mode': {'type': 'boolean', 'required': False},
                    'tuple_transformation_function': {'type': 'string', 'allowed': ['demo']},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['EventCorrelationDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'max_hypotheses': {'type': 'integer', 'required': False, 'default': 1000},
                    'hypothesis_max_delta_time': {'type': 'float', 'required': False, 'default': 5.0},
                    'generation_probability': {'type': 'float', 'required': False, 'default': 1.0},
                    'generation_factor': {'type': 'float', 'required': False, 'default': 1.0},
                    'max_observations': {'type': 'integer', 'required': False, 'default': 500},
                    'p0': {'type': 'float', 'required': False, 'default': 0.9},
                    'alpha': {'type': 'float', 'required': False, 'default': 0.05},
                    'candidates_size': {'type': 'integer', 'required': False, 'default': 10},
                    'hypotheses_eval_delta_time': {'type': 'float', 'required': False, 'default': 120.0},
                    'delta_time_to_discard_hypothesis': {'type': 'float', 'required': False, 'default': 180.0},
                    'check_rules_flag': {'type': 'boolean', 'required': False, 'default': False},
                    'learn_mode': {'type': 'boolean', 'required': False},
                    'ignore_list': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True, 'default': None},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'output_logline': {'type': 'boolean'},
                    'constraint_list': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True, 'default': None},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['EventFrequencyDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'window_size': {'type': 'integer', 'required': False, 'default': 600},
                    'confidence_factor': {'type': 'float', 'required': False, 'default': 0.5},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'learn_mode': {'type': 'boolean', 'required': False},
                    'output_logline': {'type': 'boolean'},
                    'ignore_list': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True, 'default': None},
                    'constraint_list': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True, 'default': None},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['EventSequenceDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'id_path_list': {'type': 'list', 'required': False, 'default': []},
                    'seq_len': {'type': 'integer', 'required': False, 'default': 3},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'learn_mode': {'type': 'boolean', 'required': False},
                    'output_logline': {'type': 'boolean'},
                    'ignore_list': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True, 'default': None},
                    'constraint_list': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True, 'default': None},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['EventTypeDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'min_num_vals': {'type': 'integer', 'required': False, 'default': 1000},
                    'max_num_vals': {'type': 'integer', 'required': False, 'default': 1500},
                    'save_values': {'type': 'boolean', 'required': False, 'default': True},
                    'track_time_for_TSA': {'type': 'boolean', 'required': False, 'default': False},
                    'waiting_time_for_TSA': {'type': 'integer', 'required': False, 'default': 300},
                    'num_sections_waiting_time_for_TSA': {'type': 'integer', 'required': False, 'default': 10},
                    'learn_mode': {'type': 'boolean', 'required': False},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['LinearNumericBinDefinition'], 'required': True},
                    'lower_limit': {'type': ['integer', 'float']},
                    'bin_size': {'type': 'integer'},
                    'bin_count': {'type': 'integer'},
                    'outlier_bins_flag': {'type': 'boolean', 'required': False, 'default': False},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ModuloTimeBinDefinition'], 'required': True},
                    'modulo_value': {'type': 'integer'},
                    'time_unit': {'type': 'integer'},
                    'lower_limit': {'type': ['integer', 'float']},
                    'bin_size': {'type': 'integer'},
                    'bin_count': {'type': 'integer'},
                    'outlier_bins_flag': {'type': 'boolean', 'required': False, 'default': False},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['HistogramAnalysis'], 'required': True},
                    'histogram_defs': {'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'string'}}},
                    'report_interval': {'type': 'integer', 'required': False, 'default': 10},
                    'reset_after_report_flag': {'type': 'boolean', 'required': False, 'default': True},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['PathDependentHistogramAnalysis'], 'required': True},
                    'path': {'type': 'string', 'required': False, 'default': 'Default'},
                    'bin_definition': {'type': 'string'},
                    'report_interval': {'type': 'integer', 'required': False, 'default': 10},
                    'reset_after_report_flag': {'type': 'boolean', 'required': False, 'default': True},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MatchFilter'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'value_list': {
                        'type': 'list', 'schema': {'type': ['boolean', 'float', 'integer', 'string']}, 'nullable': True, 'default': None},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MatchValueAverageChangeDetector'], 'required': True},
                    'timestamp_path': {'type': 'string'},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'min_bin_elements': {'type': 'integer'},
                    'min_bin_time': {'type': 'integer'},
                    'debug_mode': {'type': 'boolean', 'required': False, 'default': False},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MatchValueStreamWriter'], 'required': True},
                    # skipcq: PYL-W0511
                    # TODO check which streams should be allowed
                    'stream': {'type': 'string', 'allowed': ['sys.stdout', 'sys.stderr']},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'separator': {'type': 'string'},
                    'missing_value_string': {'type': 'string'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MissingMatchPathValueDetector'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'learn_mode': {'type': 'boolean', 'required': False},
                    'check_interval': {'type': 'integer', 'required': False, 'default': 3600},
                    'realert_interval': {'type': 'integer', 'required': False, 'default': 86400},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MissingMatchPathListValueDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'learn_mode': {'type': 'boolean', 'required': False},
                    'check_interval': {'type': 'integer', 'required': False, 'default': 3600},
                    'realert_interval': {'type': 'integer', 'required': False, 'default': 86400},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['NewMatchIdValueComboDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'id_path_list': {'type': 'list', 'required': False, 'default': []},
                    'min_allowed_time_diff': {'type': 'float', 'required': True},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'allow_missing_values': {'type': 'boolean', 'required': False, 'default': False},
                    'learn_mode': {'type': 'boolean', 'required': False},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['NewMatchPathDetector'], 'required': True},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'learn_mode': {'type': 'boolean', 'required': False},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['NewMatchPathValueComboDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'allow_missing_values': {'type': 'boolean', 'required': False, 'default': False},
                    'learn_mode': {'type': 'boolean', 'required': False},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['NewMatchPathValueDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'learn_mode': {'type': 'boolean', 'required': False},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ParserCount'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'report_interval': {'type': 'integer', 'required': False, 'default': 60},
                    'labels': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'split_reports_flag': {'type': 'boolean', 'required': False, 'default': False},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['AndMatchRule', 'OrMatchRule', 'ParallelMatchRule'], 'required': True},
                    'sub_rules': {'type': 'list', 'schema': {'type': 'string'}},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ValueDependentDelegatedMatchRule'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'rule_lookup_dict': {'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': 'string'}}},
                    'default_rule': {'type': 'string', 'required': False, 'nullable': True, 'default': None},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['NegationMatchRule'], 'required': True},
                    'sub_rule': {'type': 'string'},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['PathExistsMatchRule', 'IPv4InRFC1918MatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ValueMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'value': {'type': ['boolean', 'float', 'integer', 'string']},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ValueListMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'value_list': {
                        'type': 'list', 'schema': {'type': ['boolean', 'float', 'integer', 'string']}, 'nullable': True, 'default': None},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ValueRangeMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'lower_limit': {'type': ['integer', 'float']},
                    'upper_limit': {'type': ['integer', 'float']},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['StringRegexMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'regex': {'type': 'string'},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ModuloTimeMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'seconds_modulo': {'type': 'integer'},
                    'lower_limit': {'type': ['integer', 'float']},
                    'upper_limit': {'type': ['integer', 'float']},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ValueDependentModuloTimeMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'seconds_modulo': {'type': 'integer'},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'limit_lookup_dict': {
                        'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': 'list', 'schema': {'type': 'integer'}}}},
                    'default_limit': {'type': 'list', 'schema': {'type': 'integer'}, 'required': False, 'nullable': True, 'default': None},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['DebugMatchRule', 'DebugHistoryMatchRule'], 'required': True},
                    'debug_mode': {'type': 'boolean', 'required': False, 'default': False},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['TimeCorrelationDetector'], 'required': True},
                    'parallel_check_count': {'type': 'integer', 'required': True},
                    'record_count_before_event': {'type': 'integer', 'required': False, 'default': 10000},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'output_logline': {'type': 'boolean'},
                    'use_path_match': {'type': 'boolean', 'required': False, 'default': True},
                    'use_value_match': {'type': 'boolean', 'required': False, 'default': True},
                    'min_rule_attributes': {'type': 'integer', 'required': False, 'default': 1},
                    'max_rule_attributes': {'type': 'integer', 'required': False, 'default': 5},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['TimeCorrelationViolationDetector'], 'required': True},
                    'ruleset': {'type': 'list', 'schema': {'type': 'string'}},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'type': {'type': 'string', 'allowed': ['CorrelationRule'], 'required': True},
                    'rule_id': {'type': 'string'},
                    'min_time_delta': {'type': 'integer'},
                    'max_time_delta': {'type': 'integer'},
                    'max_artefacts_a_for_single_b': {'type': 'integer'},
                    'artefact_match_parameters': {'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'string'}},
                                                  'required': False, 'nullable': True, 'default': None}
                },
                {
                    'type': {'type': 'string', 'allowed': ['EventClassSelector'], 'required': True},
                    'action_id': {'type': 'string'},
                    'artefact_a_rules': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'artefact_b_rules': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['SimpleMonotonicTimestampAdjust'], 'required': True},
                    'stop_when_handled_flag': {'type': 'boolean', 'required': False, 'default': False},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['TimestampsUnsortedDetector'], 'required': True},
                    'exit_on_error_flag': {'type': 'boolean', 'required': False, 'default': False},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['VariableCorrelationDetector'], 'required': True},
                    'event_type_detector': {'type': 'string'},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'num_init': {'type': 'integer', 'required': False, 'default': 100},
                    'num_update': {'type': 'integer', 'required': False, 'default': 100},
                    'disc_div_thres': {'type': 'float', 'required': False, 'default': 0.3},
                    'num_steps_create_new_rules': {'type': ['boolean', 'integer'], 'required': False, 'default': False},
                    'num_upd_until_validation': {'type': 'integer', 'required': False, 'default': 20},
                    'num_end_learning_phase': {'type': ['boolean', 'integer'], 'required': False, 'default': False},
                    'check_cor_thres': {'type': 'float', 'required': False, 'default': 0.5},
                    'check_cor_prob_thres': {'type': 'float', 'required': False, 'default': 1.0},
                    'check_cor_num_thres': {'type': 'integer', 'required': False, 'default': 10},
                    'min_values_cors_thres': {'type': 'integer', 'required': False, 'default': 5},
                    'new_vals_alarm_thres': {'type': 'float', 'required': False, 'default': 3.5},
                    'num_bt': {'type': 'integer', 'required': False, 'default': 30},
                    'alpha_bt': {'type': 'float', 'required': False, 'default': 0.1},
                    'used_homogeneity_test': {'type': 'string', 'allowed': ['Chi', 'MaxDist'], 'required': False, 'default': 'Chi'},
                    'alpha_chisquare_test': {'type': 'float', 'required': False, 'default': 0.05},
                    'max_dist_rule_distr': {'type': 'float', 'required': False, 'default': 0.1},
                    'used_presel_meth': {'type': 'list', 'required': False, 'schema': {'type': 'string', 'allowed': [
                        'matchDiscDistr', 'excludeDueDistr', 'matchDiscVals', 'random']}, 'nullable': True, 'default': None},
                    'intersect_presel_meth': {'type': 'boolean', 'required': False, 'default': False},
                    'percentage_random_cors': {'type': 'float', 'required': False, 'default': 0.20},
                    'match_disc_vals_sim_tresh': {'type': 'float', 'required': False, 'default': 0.7},
                    'exclude_due_distr_lower_limit': {'type': 'float', 'required': False, 'default': 0.4},
                    'match_disc_distr_threshold': {'type': 'float', 'required': False, 'default': 0.5},
                    'used_cor_meth': {'type': 'list', 'required': False, 'schema': {'type': 'string', 'allowed': ['Rel', 'WRel']},
                                      'nullable': True, 'default': None},
                    'used_validate_cor_meth': {'type': 'list', 'required': False, 'schema': {'type': 'string', 'allowed': [
                        'coverVals', 'distinctDistr']}, 'nullable': True, 'default': None},
                    'validate_cor_cover_vals_thres': {'type': 'float', 'required': False, 'default': 0.7},
                    'validate_cor_distinct_thres': {'type': 'float', 'required': False, 'default': 0.05},
                    'constraint_list': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True, 'default': None},
                    'ignore_list': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True, 'default': None},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['VariableTypeDetector'], 'required': True},
                    'event_type_detector': {'type': 'string'},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'ks_alpha': {'type': 'float', 'required': False, 'default': 0.05},
                    's_ks_alpha': {'type': 'float', 'required': False, 'default': 0.05},
                    's_ks_bt_alpha': {'type': 'float', 'required': False, 'default': 0.05},
                    'd_alpha': {'type': 'float', 'required': False, 'default': 0.1},
                    'd_bt_alpha': {'type': 'float', 'required': False, 'default': 0.1},
                    'div_thres': {'type': 'float', 'required': False, 'default': 0.3},
                    'sim_thres': {'type': 'float', 'required': False, 'default': 0.1},
                    'indicator_thres': {'type': 'float', 'required': False, 'default': 0.4},
                    'num_init': {'type': 'integer', 'required': False, 'default': 100},
                    'num_update': {'type': 'integer', 'required': False, 'default': 50},
                    'num_update_unq': {'type': 'integer', 'required': False, 'default': 200},
                    'num_s_ks_values': {'type': 'integer', 'required': False, 'default': 50},
                    'num_s_ks_bt': {'type': 'integer', 'required': False, 'default': 30},
                    'num_d_bt': {'type': 'integer', 'required': False, 'default': 30},
                    'num_pause_discrete': {'type': 'integer', 'required': False, 'default': 5},
                    'num_pause_others': {'type': 'integer', 'required': False, 'default': 2},
                    'test_ks_int': {'type': 'boolean', 'required': False, 'default': True},
                    'update_var_type_bool': {'type': 'boolean', 'required': False, 'default': True},
                    'num_stop_update': {'type': 'boolean', 'required': False, 'default': False},
                    'silence_output_without_confidence': {'type': 'boolean', 'required': False, 'default': False},
                    'silence_output_except_indicator': {'type': 'boolean', 'required': False, 'default': True},
                    'num_var_type_hist_ref': {'type': 'integer', 'required': False, 'default': 10},
                    'num_update_var_type_hist_ref': {'type': 'integer', 'required': False, 'default': 10},
                    'num_var_type_considered_ind': {'type': 'integer', 'required': False, 'default': 10},
                    'num_stat_stop_update': {'type': 'integer', 'required': False, 'default': 200},
                    'num_updates_until_var_reduction': {'type': 'integer', 'required': False, 'default': 20},
                    'var_reduction_thres': {'type': 'float', 'required': False, 'default': 0.6},
                    'num_skipped_ind_for_weights': {'type': 'integer', 'required': False, 'default': 1},
                    'num_ind_for_weights': {'type': 'integer', 'required': False, 'default': 100},
                    'used_multinomial_test': {'type': 'string', 'allowed': ['Approx', 'MT', 'Chi'], 'required': False, 'default': 'Chi'},
                    'use_empiric_distr': {'type': 'boolean', 'required': False, 'default': True},
                    'save_statistics': {'type': 'boolean', 'required': False, 'default': True},
                    'output_logline': {'type': 'boolean'},
                    'constraint_list': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True, 'default': None},
                    'ignore_list': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True, 'default': None},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                }
            ]
        }
    }
}
