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
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'required': True},
                    'persistence_id': {'type': 'string'},
                    'allow_missing_values': {'type': 'boolean'},
                    'learn_mode': {'type': 'boolean'},
                    'tuple_transformation_function': {'type': 'string', 'allowed': ['demo'], 'nullable': True},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['EventCorrelationDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'max_hypotheses': {'type': 'integer', 'min': 1},
                    'hypothesis_max_delta_time': {'type': 'float', 'min': 0.01},
                    'generation_probability': {'type': 'float', 'min': 0, 'max': 1},
                    'generation_factor': {'type': 'float', 'min': 0, 'max': 1},
                    'max_observations': {'type': 'integer', 'min': 1},
                    'p0': {'type': 'float', 'min': 0, 'max': 1},
                    'alpha': {'type': 'float', 'min': 0, 'max': 1},
                    'candidates_size': {'type': 'integer', 'min': 1},
                    'hypotheses_eval_delta_time': {'type': 'float', 'min': 0.01},
                    'delta_time_to_discard_hypothesis': {
                        'type': 'float', 'min': 0.01, 'bigger_than_or_equal': ['hypotheses_eval_delta_time', 120.0]},
                    'check_rules_flag': {'type': 'boolean'},
                    'learn_mode': {'type': 'boolean'},
                    'ignore_list': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'persistence_id': {'type': 'string'},
                    'output_logline': {'type': 'boolean'},
                    'constraint_list': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['EventFrequencyDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'window_size': {'type': 'integer', 'min': 1},
                    'confidence_factor': {'type': 'float', 'min': 0, 'max': 1},
                    'persistence_id': {'type': 'string'},
                    'learn_mode': {'type': 'boolean'},
                    'output_logline': {'type': 'boolean'},
                    'ignore_list': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'constraint_list': {'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['EventSequenceDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'id_path_list': {'type': 'list', 'required': True},
                    'seq_len': {'type': 'integer', 'min': 1},
                    'persistence_id': {'type': 'string'},
                    'learn_mode': {'type': 'boolean'},
                    'output_logline': {'type': 'boolean'},
                    'ignore_list': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'constraint_list': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['EventTypeDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'persistence_id': {'type': 'string'},
                    'min_num_vals': {'type': 'integer', 'min': 1},
                    'max_num_vals': {'type': 'integer', 'min': 1, 'bigger_than_or_equal': ['min_num_vals', 1000]},
                    'save_values': {'type': 'boolean'},
                    'track_time_for_TSA': {'type': 'boolean'},
                    'waiting_time_for_TSA': {'type': 'integer', 'min': 1},
                    'num_sections_waiting_time_for_TSA': {'type': 'integer', 'min': 1},
                    'learn_mode': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['LinearNumericBinDefinition'], 'required': True},
                    'lower_limit': {'type': ['integer', 'float'], 'required': True},
                    'bin_size': {'type': 'integer', 'required': True, 'min': 1},
                    'bin_count': {'type': 'integer', 'required': True, 'min': 1},
                    'outlier_bins_flag': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ModuloTimeBinDefinition'], 'required': True},
                    'modulo_value': {'type': ['integer', 'float'], 'required': True, 'min': 0.000001},
                    'time_unit': {'type': 'integer', 'required': True, 'min': 1},
                    'lower_limit': {'type': ['integer', 'float'], 'required': True, 'min': 0},
                    'bin_size': {'type': 'integer', 'required': True, 'min': 1},
                    'bin_count': {'type': 'integer', 'required': True, 'min': 1},
                    'outlier_bins_flag': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['HistogramAnalysis'], 'required': True},
                    'histogram_defs': {'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'string'}}, 'required': True},
                    'report_interval': {'type': 'integer', 'required': True, 'min': 1},
                    'reset_after_report_flag': {'type': 'boolean'},
                    'persistence_id': {'type': 'string'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['PathDependentHistogramAnalysis'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'bin_definition': {'type': 'string', 'required': True},
                    'report_interval': {'type': 'integer', 'required': True, 'min': 1},
                    'reset_after_report_flag': {'type': 'boolean'},
                    'persistence_id': {'type': 'string'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MatchFilter'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'value_list': {
                        'type': 'list', 'schema': {'type': ['boolean', 'float', 'integer', 'string']}, 'nullable': True},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MatchValueAverageChangeDetector'], 'required': True},
                    'timestamp_path': {'type': 'string', 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'min_bin_elements': {'type': 'integer', 'required': True, 'min': 1},
                    'min_bin_time': {'type': 'integer', 'required': True, 'min': 1},
                    'debug_mode': {'type': 'boolean'},
                    'persistence_id': {'type': 'string'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MatchValueStreamWriter'], 'required': True},
                    'stream': {'type': 'string', 'allowed': ['sys.stdout', 'sys.stderr'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'separator': {'type': 'string', 'required': True},
                    'missing_value_string': {'type': 'string', 'required': True},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MissingMatchPathValueDetector'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'persistence_id': {'type': 'string'},
                    'learn_mode': {'type': 'boolean'},
                    'check_interval': {'type': 'integer', 'min': 1},
                    'realert_interval': {'type': 'integer', 'min': 1, 'bigger_than_or_equal': ['check_interval', 3600]},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['MissingMatchPathListValueDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'persistence_id': {'type': 'string'},
                    'learn_mode': {'type': 'boolean'},
                    'check_interval': {'type': 'integer', 'min': 1},
                    'realert_interval': {'type': 'integer', 'min': 1, 'bigger_than_or_equal': ['check_interval', 3600]},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['NewMatchIdValueComboDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'id_path_list': {'type': 'list', 'required': True},
                    'min_allowed_time_diff': {'type': 'float', 'required': True, 'min': 0.01},
                    'persistence_id': {'type': 'string'},
                    'allow_missing_values': {'type': 'boolean'},
                    'learn_mode': {'type': 'boolean'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['NewMatchPathDetector'], 'required': True},
                    'persistence_id': {'type': 'string'},
                    'learn_mode': {'type': 'boolean'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['NewMatchPathValueComboDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'persistence_id': {'type': 'string'},
                    'allow_missing_values': {'type': 'boolean'},
                    'learn_mode': {'type': 'boolean'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['NewMatchPathValueDetector'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'persistence_id': {'type': 'string'},
                    'learn_mode': {'type': 'boolean'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ParserCount'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}},
                    'report_interval': {'type': 'integer', 'min': 1},
                    'labels': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'split_reports_flag': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['AndMatchRule', 'OrMatchRule', 'ParallelMatchRule'], 'required': True},
                    'sub_rules': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'match_action': {'type': 'string', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ValueDependentDelegatedMatchRule'], 'required': True},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'rule_lookup_dict': {
                        'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': 'string'}}, 'required': True},
                    'default_rule': {'type': 'string', 'nullable': True},
                    'match_action': {'type': 'string', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['NegationMatchRule'], 'required': True},
                    'sub_rule': {'type': 'string', 'required': True},
                    'match_action': {'type': 'string', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['PathExistsMatchRule', 'IPv4InRFC1918MatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'match_action': {'type': 'string', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ValueMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'value': {'type': ['boolean', 'float', 'integer', 'string'], 'required': True},
                    'match_action': {'type': 'string', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ValueListMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'value_list': {
                        'type': 'list', 'schema': {'type': ['boolean', 'float', 'integer', 'string']}, 'required': True},
                    'match_action': {'type': 'string', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ValueRangeMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'lower_limit': {'type': ['integer', 'float'], 'required': True},
                    'upper_limit': {'type': ['integer', 'float'], 'required': True, 'bigger_than_or_equal': ['lower_limit', None]},
                    'match_action': {'type': 'string', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['StringRegexMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'regex': {'type': 'string', 'required': True},
                    'match_action': {'type': 'string', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ModuloTimeMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'seconds_modulo': {'type': 'integer', 'required': True, 'min': 1},
                    'lower_limit': {'type': ['integer', 'float'], 'required': True, 'min': 0},
                    'upper_limit': {
                        'type': ['integer', 'float'], 'required': True, 'min': 0, 'bigger_than_or_equal': ['lower_limit', None]},
                    'match_action': {'type': 'string', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['ValueDependentModuloTimeMatchRule'], 'required': True},
                    'path': {'type': 'string', 'required': True},
                    'seconds_modulo': {'type': 'integer', 'required': True, 'min': 1},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'limit_lookup_dict': {'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': 'list', 'schema': {
                        'type': 'integer', 'min': 0}}}, 'required': True},
                    'default_limit': {'type': 'list', 'schema': {'type': 'integer', 'min': 0}, 'nullable': True},
                    'match_action': {'type': 'string', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['DebugMatchRule', 'DebugHistoryMatchRule'], 'required': True},
                    'debug_mode': {'type': 'boolean'},
                    'match_action': {'type': 'string', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['TimeCorrelationDetector'], 'required': True},
                    'parallel_check_count': {'type': 'integer', 'required': True, 'min': 1},
                    'record_count_before_event': {'type': 'integer', 'min': 1},
                    'persistence_id': {'type': 'string'},
                    'output_logline': {'type': 'boolean'},
                    'use_path_match': {'type': 'boolean'},
                    'use_value_match': {'type': 'boolean'},
                    'min_rule_attributes': {'type': 'integer', 'min': 1},
                    'max_rule_attributes': {'type': 'integer', 'min': 1, 'bigger_than_or_equal': ['min_rule_attributes', 1]},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['TimeCorrelationViolationDetector'], 'required': True},
                    'ruleset': {'type': 'list', 'schema': {'type': 'string'}, 'required': True},
                    'persistence_id': {'type': 'string'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'type': {'type': 'string', 'allowed': ['CorrelationRule'], 'required': True},
                    'rule_id': {'type': 'string', 'required': True},
                    'min_time_delta': {'type': 'integer', 'required': True, 'min': 1},
                    'max_time_delta': {'type': 'integer', 'required': True, 'min': 1, 'bigger_than_or_equal': ['min_time_delta', None]},
                    'max_artefacts_a_for_single_b': {'type': 'integer', 'min': 1},
                    'artefact_match_parameters': {'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'string'}},
                                                  'nullable': True}
                },
                {
                    'type': {'type': 'string', 'allowed': ['EventClassSelector'], 'required': True},
                    'action_id': {'type': 'string', 'required': True},
                    'artefact_a_rules': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'artefact_b_rules': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['SimpleMonotonicTimestampAdjust'], 'required': True},
                    'stop_when_handled_flag': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['TimestampsUnsortedDetector'], 'required': True},
                    'exit_on_error_flag': {'type': 'boolean'},
                    'output_logline': {'type': 'boolean'},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['VariableCorrelationDetector'], 'required': True},
                    'event_type_detector': {'type': 'string', 'required': True},
                    'persistence_id': {'type': 'string'},
                    'num_init': {'type': 'integer', 'min': 1},
                    'num_update': {'type': 'integer', 'min': 1},
                    'disc_div_thres': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'num_steps_create_new_rules': {'type': 'integer', 'min': 1},
                    'num_upd_until_validation': {'type': 'integer', 'min': 1},
                    'num_end_learning_phase': {'type': 'integer', 'min': 1},
                    'check_cor_thres': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'check_cor_prob_thres': {'type': 'float', 'min': 0.000001},
                    'check_cor_num_thres': {'type': 'integer', 'min': 1},
                    'min_values_cors_thres': {'type': 'integer', 'min': 1},
                    'new_vals_alarm_thres': {'type': 'float', 'min': 0.000001},
                    'num_bt': {'type': 'integer', 'min': 1},
                    'alpha_bt': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'used_homogeneity_test': {'type': 'string', 'allowed': ['Chi', 'MaxDist']},
                    'alpha_chisquare_test': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'max_dist_rule_distr': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'used_presel_meth': {'type': 'list', 'schema': {'type': 'string', 'allowed': [
                        'matchDiscDistr', 'excludeDueDistr', 'matchDiscVals', 'random']}, 'nullable': True},
                    'intersect_presel_meth': {'type': 'boolean'},
                    'percentage_random_cors': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'match_disc_vals_sim_tresh': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'exclude_due_distr_lower_limit': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'match_disc_distr_threshold': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'used_cor_meth': {'type': 'list', 'schema': {'type': 'string', 'allowed': ['Rel', 'WRel']}, 'nullable': True},
                    'used_validate_cor_meth': {'type': 'list', 'schema': {'type': 'string', 'allowed': [
                        'coverVals', 'distinctDistr']}, 'nullable': True},
                    'validate_cor_cover_vals_thres': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'validate_cor_distinct_thres': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'constraint_list': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'ignore_list': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'nullable': True},
                    'type': {'type': 'string', 'allowed': ['VariableTypeDetector'], 'required': True},
                    'event_type_detector': {'type': 'string', 'required': True},
                    'persistence_id': {'type': 'string'},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'ks_alpha': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    's_ks_alpha': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    's_ks_bt_alpha': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'd_alpha': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'd_bt_alpha': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'div_thres': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'sim_thres': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'indicator_thres': {'type': 'float', 'min': 0.000001, 'max': 1.0},
                    'num_init': {'type': 'integer', 'min': 1},
                    'num_update': {'type': 'integer', 'min': 1},
                    'num_update_unq': {'type': 'integer', 'min': 1},
                    'num_s_ks_values': {'type': 'integer', 'min': 1},
                    'num_s_ks_bt': {'type': 'integer', 'min': 1},
                    'num_d_bt': {'type': 'integer', 'min': 1},
                    'num_pause_discrete': {'type': 'integer', 'min': 0},
                    'num_pause_others': {'type': 'integer', 'min': 0},
                    'test_ks_int': {'type': 'boolean'},
                    'update_var_type_bool': {'type': 'boolean'},
                    'num_stop_update': {'type': 'boolean'},
                    'silence_output_without_confidence': {'type': 'boolean'},
                    'silence_output_except_indicator': {'type': 'boolean'},
                    'num_var_type_hist_ref': {'type': 'integer', 'min': 1},
                    'num_update_var_type_hist_ref': {'type': 'integer', 'min': 1},
                    'num_var_type_considered_ind': {'type': 'integer', 'min': 1},
                    'num_stat_stop_update': {'type': 'integer', 'min': 1},
                    'num_updates_until_var_reduction': {'type': 'integer', 'min': 1},
                    'var_reduction_thres': {'type': 'float'},
                    'num_skipped_ind_for_weights': {'type': 'integer', 'min': 0},
                    'num_ind_for_weights': {'type': 'integer', 'min': 1},
                    'used_multinomial_test': {'type': 'string', 'allowed': ['Approx', 'MT', 'Chi'], },
                    'use_empiric_distr': {'type': 'boolean'},
                    'save_statistics': {'type': 'boolean'},
                    'output_logline': {'type': 'boolean'},
                    'constraint_list': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'ignore_list': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True},
                    'output_event_handlers': {'type': 'list', 'nullable': True},
                    'suppress': {'type': 'boolean'}
                }
            ]
        }
    }
}
