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
                'TimestampPath': {'type': 'string'}
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
                              'MissingMatchPathListValueDetector', 'TimeCorrelationDetector']},
                     'paths': {'type': 'list', 'schema': {'type': 'string'}},
                     'learnMode': {'type': 'boolean'},
                     'persistence_id': {'type': 'string', 'required': False, 'default': 'Default'},
                     'output_logline': {'type': 'boolean', 'required': False, 'default': True},
                     'allow_missing_values': {'type': 'boolean', 'required': False, 'default': False},
                     'check_interval': {'type': 'integer', 'required': False, 'default': 3600},
                     'realert_interval': {'type': 'integer', 'required': False, 'default': 36000},
                     'path': {'type': 'string', 'required': False, 'default': 'Default'},
                     'parallel_check_count': {'type': 'integer', 'required': True, 'default': 10},
                     'record_count_before_event': {'type': 'integer', 'required': False, 'default': 1000},
                     'use_path_match': {'type': 'boolean', 'required': False, 'default': True},
                     'use_value_match': {'type': 'boolean', 'required': False, 'default': True},
                     'min_rule_attributes': {'type': 'integer', 'required': False, 'default': 1},
                     'max_rule_attributes': {'type': 'integer', 'required': False, 'default': 5}
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

