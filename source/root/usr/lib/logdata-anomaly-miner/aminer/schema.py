# skipcq: PYL-W0104
{
        'LearnMode': {
            'required': False,
            'type': 'boolean'
        },
        'AMinerUser': {
            'required': False,
            'type': 'string',
            'default': 'aminer'
        },
        'AMinerGroup': {
            'required': False,
            'type': 'string',
            'default': 'aminer'
        },
        'Core.PersistenceDir': {
            'required': False,
            'type': 'string',
            'default': '/var/lib/aminer'
        },
        'MailAlerting.TargetAddress': {
            'required': False,
            'type': 'string',
            'default': 'root@localhost'
        },
        'MailAlerting.FromAddress': {
            'required': False,
            'type': 'string',
            'default': 'root@localhost'
        },
        'MailAlerting.SubjectPrefix': {
            'required': False,
            'type': 'string',
            'default': 'AMiner Alerts:'
        },
        'MailAlerting.AlertGraceTime': {
            'required': False,
            'type': 'integer',
            'default': 0
        },
        'MailAlerting.EventCollectTime': {
            'required': False,
            'type': 'integer',
            'default': 10
        },
        'MailAlerting.MinAlertGap': {
            'required': False,
            'type': 'integer',
            'default': 600
        },
        'MailAlerting.MaxAlertGap': {
            'required': False,
            'type': 'integer',
            'default': 600
        },
        'MailAlerting.MaxEventsPerMessage': {
            'required': False,
            'type': 'integer',
            'default': 1000
        },
        'LogPrefix': {
            'required': False,
            'type': 'string',
        },
        'LogResourceList': {
            'required': True,
            'type': 'list',
            'schema': {'type': 'string'}
        },
        'Parser': {
            'required': True,
            'type': 'list',
            'has_start': True,
            'schema': {
                'type': 'dict',
                'schema': {
                    'id': {'type': 'string'},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'parsermodel', 'coerce': 'toparsermodel'},
                    'name': {'type': 'string'},
                    'args': {'type': ['string', 'list'], 'schema': {'type': ['string', 'integer']}, 'nullable': True},
                    'branch_model_dict': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'id': {
                        'type': ['boolean', 'float', 'integer', 'string']}, 'model': {'type': 'string'}}}},
                    'date_formats': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'format': {'type': 'list', 'schema': {
                        'type': 'string', 'nullable': True}}}}},
                    'value_sign_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory'], 'default': 'none'},
                    'value_pad_type': {'type': 'string', 'allowed': ['none', 'zero', 'blank'], 'default': 'none'},
                    'exponent_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory'], 'default': 'none'}
                }
            }
        },
        'Input': {
            'required': True,
            'type': 'dict',
            'schema': {
                'verbose': {'type': 'boolean', 'required': False, 'default': False},
                'multi_source': {'type': 'boolean', 'required': False, 'default': False},
                'timestamp_paths': {'type': ['string', 'list']}
            }
        },
        'Analysis': {
            'required': False,
            'type': 'list',
            'nullable': True,
            'schema': {
                'type': 'dict',
                'schema': {
                    'id': {'type': 'string', 'required': False, 'nullable': True, 'default': None},
                    'type': {'type': 'analysistype', 'coerce': 'toanalysistype'},
                    'paths': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                    'output_logline': {'type': 'boolean', 'required': False, 'default': True},
                    'allow_missing_values': {'type': 'boolean', 'required': False, 'default': False},
                    'check_interval': {'type': 'integer', 'required': False, 'default': 3600},
                    'realert_interval': {'type': 'integer', 'required': False, 'default': 36000},
                    'report_interval': {'type': 'integer', 'required': False, 'default': 10},
                    'reset_after_report_flag': {'type': 'boolean', 'required': False, 'default': False},
                    'path': {'type': 'string', 'required': False, 'default': 'Default'},
                    'parallel_check_count': {'type': 'integer', 'required': True, 'default': 10},
                    'record_count_before_event': {'type': 'integer', 'required': False, 'default': 1000},
                    'use_path_match': {'type': 'boolean', 'required': False, 'default': True},
                    'use_value_match': {'type': 'boolean', 'required': False, 'default': True},
                    'min_rule_attributes': {'type': 'integer', 'required': False, 'default': 1},
                    'max_rule_attributes': {'type': 'integer', 'required': False, 'default': 5},
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
                    'check_rules_flag': {'type': 'boolean', 'required': False, 'default': True},
                    'auto_include_flag': {'type': 'boolean', 'required': False, 'default': True},
                    'whitelisted_paths': {
                        'type': 'list', 'schema': {'type': 'string'}, 'required': False, 'nullable': True, 'default': None},
                    'id_path_list': {'type': 'list', 'required': False, 'default': []},
                    'min_allowed_time_diff': {'type': 'float', 'required': False, 'default': 5.0},
                    'lower_limit': {'type': ['integer', 'float']},
                    'upper_limit': {'type': ['integer', 'float']},
                    'bin_size': {'type': 'integer'},
                    'bin_count': {'type': 'integer'},
                    'outlier_bins_flag': {'type': 'boolean', 'required': False, 'default': False},
                    'modulo_value': {'type': 'integer'},
                    'time_unit': {'type': 'integer'},
                    'histogram_defs': {'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'string'}}},
                    'bin_definition': {'type': 'string'},
                    'tuple_transformation_function': {'type': 'string'},
                    'value_list': {'type': 'list', 'schema': {'type': ['boolean', 'float', 'integer', 'string']}},
                    'timestamp_path': {'type': 'string'},
                    'min_bin_elements': {'type': 'integer'},
                    'min_bin_time': {'type': 'integer'},
                    'sync_bins_flag': {'type': 'boolean', 'required': False, 'default': True},
                    'debug_mode': {'type': 'boolean', 'required': False, 'default': False},
                    # skipcq: PYL-W0511
                    # TODO check which streams should be allowed
                    'stream': {'type': 'string', 'allowed': ['sys.stdout', 'sys.stderr']},
                    'separator': {'type': 'string'},
                    'missing_value_string': {'type': 'string'},
                    'event_type': {'type': 'string'},
                    'event_message': {'type': 'string'},
                    'stop_when_handled_flag': {'type': 'boolean', 'required': False, 'default': False},
                    'sub_rules': {'type': 'list', 'schema': {'type': 'string'}},
                    'sub_rule': {'type': 'string'},
                    'match_action': {'type': 'string', 'required': False, 'nullable': True, 'default': None},
                    'rule_lookup_dict': {'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': 'string'}}},
                    'default_rule': {'type': 'string', 'required': False, 'nullable': True, 'default': None},
                    'value': {'type': ['boolean', 'float', 'integer', 'string']},
                    'regex': {'type': 'string'},
                    'seconds_modulo': {'type': 'integer'},
                    'limit_lookup_dict': {
                        'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': 'list', 'schema': {'type': 'integer'}}}},
                    'default_limit': {'type': 'list', 'schema': {'type': 'integer'}, 'required': False, 'nullable': True, 'default': None},
                    'rule_id': {'type': 'string'},
                    'min_time_delta': {'type': 'integer'},
                    'max_time_delta': {'type': 'integer'},
                    'max_artefacts_a_for_single_b': {'type': 'integer'},
                    'artefact_match_parameters': {'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'string'}},
                                                  'required': False, 'nullable': True, 'default': None},
                    'action_id': {'type': 'string'},
                    'artefact_a_rules': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'artefact_b_rules': {'type': 'list', 'schema': {'type': 'string'}, 'nullable': True, 'default': None},
                    'ruleset': {'type': 'list', 'schema': {'type': 'string'}},
                    'exit_on_error_flag': {'type': 'boolean', 'required': False, 'default': False},
                    'whitelist_rules': {'type': 'list', 'schema': {'type': 'string'}},
                    'parsed_atom_handler_lookup_list': {
                        'type': 'list', 'schema': {'type': 'list', 'schema': {'type': 'string', 'nullable': True}}},
                    'default_parsed_atom_handler': {'type': 'string', 'required': False, 'nullable': True, 'default': None},
                    'parsed_atom_handler_dict': {'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': 'string'}}},
                    'min_num_vals': {'type': 'integer', 'required': False, 'default': 1000},
                    'max_num_vals': {'type': 'integer', 'required': False, 'default': 1500},
                    'save_values': {'type': 'boolean', 'required': False, 'default': True},
                    'track_time_for_TSA': {'type': 'boolean', 'required': False, 'default': False},
                    'waiting_time_for_TSA': {'type': 'integer', 'required': False, 'default': 300},
                    'num_sections_waiting_time_for_TSA': {'type': 'integer', 'required': False, 'default': 10},
                    'event_type_detector': {'type': 'string'},
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
                }
            }
        },
        'EventHandlers': {
            'required': False,
            'type': 'list',
            'nullable': True,
            'default': None,
            'schema': {
                'type': 'dict',
                'schema': {
                    'id': {'type': 'string'},
                    'type': {'type': 'eventhandlertype', 'coerce': 'toeventhandlertype'},
                    'json': {'type': 'boolean', 'required': False, 'default': False},
                    'instance_name': {'type': 'string', 'required': False, 'default': 'aminer'},
                    'topic': {'type': 'string'},
                    'options': {'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': ['string', 'list', 'integer']}}}
                }
            }
        }
}

