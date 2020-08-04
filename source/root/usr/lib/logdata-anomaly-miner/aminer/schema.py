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
            'type': 'string'
        },
        'MailAlerting.FromAddress': {
            'required': False,
            'type': 'string'
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
            'schema': {
                'type': 'dict',
                 'schema': {
                    'id': {'type': 'string'},
                    'type': {'type': 'string'},
                    'name': {'type': 'string'},
                    'args': {'type': ['string', 'list'], 'schema': {'type': 'string'}}
                }
            }
        },
        'Input': {
            'required': True,
            'type': 'dict',
            'schema': {
                'Verbose': {'type': 'boolean', 'required': False, 'default': False},
                'MultiSource': {'type': 'boolean', 'required': False, 'default': False},
                'TimestampPath': {'type': ['string', 'list']}
            }
        },
        'Analysis': {
            'required' : True,
            'type': 'list',
            'schema': {
                'type': 'dict',
                 'schema': {
                     'id': {'type': 'string', 'required': False, 'default': 'None'},
                     'type': {'type': 'string', 'allowed': ['NewMatchPathValueDetector', 
                              'NewMatchPathValueComboDetector', 'MissingMatchPathValueDetector',
                              'MissingMatchPathListValueDetector', 'TimeCorrelationDetector',
                              'ParserCount', 'EventCorrelationDetector',
                              'NewMatchIdValueComboDetector', 'EventCorrelationDetector',
                              'ParserCount']},
                     'paths': {'type': 'list', 'schema': {'type': 'string'}},
                     'learnMode': {'type': 'boolean'},
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
                     #'whitelisted_paths': {'type': ['string', 'list', 'null'], 'required': False, 'default': None}, # TODO default None value not working
                     'id_path_list': {'type': 'list', 'required': False, 'default': []},
                     'min_allowed_time_diff': {'type': 'float', 'required': False, 'default': 5.0},
                }
            }
        },
        'EventHandlers': {
            'required': False,
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'id': {'type': 'string'},
                    'type': {'type': 'string', 'allowed': ['StreamPrinterEventHandler', 'SyslogWriterEventHandler']},
                    'json': {'type': 'boolean', 'required': False, 'default': False},
                    'args': {'type': ['string', 'list'], 'schema': {'type': 'string'}}
                }
            }
        }
}

