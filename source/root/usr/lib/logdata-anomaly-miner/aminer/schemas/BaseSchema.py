# skipcq: PYL-W0104
{
        'LearnMode': {
            'required': False,
            'type': 'boolean'
        },
        'SuppressNewMatchPathDetector': {
            'required': False,
            'type': 'boolean',
            'default': False
        },
        'AminerUser': {
            'required': False,
            'type': 'string',
            'default': 'aminer'
        },
        'AminerGroup': {
            'required': False,
            'type': 'string',
            'default': 'aminer'
        },
        'RemoteControlSocket': {
            'required': False,
            'type': 'string'
        },
        'Core.PersistenceDir': {
            'required': False,
            'type': 'string',
            'default': '/var/lib/aminer'
        },
        'Core.LogDir': {
            'required': False,
            'type': 'string',
            'default': '/var/lib/aminer/log'
        },
        'Core.PersistencePeriod': {
            'required': False,
            'type': 'integer',
            'default': 600,
            'min': 1
        },
        'MailAlerting.TargetAddress': {
            'required': False,
            'type': 'string',
            'regex': '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-]+$)|^[a-zA-Z0-9]+@localhost$',
            'default': 'root@localhost'
        },
        'MailAlerting.FromAddress': {
            'required': False,
            'type': 'string',
            'regex': '(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-]+$)|^[a-zA-Z0-9]+@localhost$',
            'default': 'root@localhost'
        },
        'MailAlerting.SubjectPrefix': {
            'required': False,
            'type': 'string',
            'default': 'aminer Alerts:'
        },
        'MailAlerting.AlertGraceTime': {
            'required': False,
            'type': 'integer',
            'default': 0,
            'min': 0
        },
        'MailAlerting.EventCollectTime': {
            'required': False,
            'type': 'integer',
            'default': 10,
            'min': 0
        },
        'MailAlerting.MinAlertGap': {
            'required': False,
            'type': 'integer',
            'default': 600,
            'min': 0
        },
        'MailAlerting.MaxAlertGap': {
            'required': False,
            'type': 'integer',
            'default': 600,
            'min': 0
        },
        'MailAlerting.MaxEventsPerMessage': {
            'required': False,
            'type': 'integer',
            'default': 1000,
            'min': 0
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
        'Log.StatisticsPeriod': {
            'required': False,
            'type': 'integer',
            'default': 3600,
            'min': 0
        },
        'Log.StatisticsLevel': {
            'required': False,
            'type': 'integer',
            'default': 1,
            'min': 0,
            'max': 2
        },
        'Log.DebugLevel': {
            'required': False,
            'type': 'integer',
            'default': 1,
            'min': 0,
            'max': 2
        },
        'Log.RemoteControlLogFile': {
            'required': False,
            'type': 'string'
        },
        'Log.StatisticsFile': {
            'required': False,
            'type': 'string'
        },
        'Log.DebugFile': {
            'required': False,
            'type': 'string'
        },
        'Input': {
            'required': True,
            'type': 'dict',
            'schema': {
                'verbose': {'type': 'boolean', 'required': False, 'default': True},
                'multi_source': {'type': 'boolean', 'required': False, 'default': False},
                'timestamp_paths': {'type': ['string', 'list']},
                'sync_wait_time': {'type': 'integer', 'min': 1, 'default': 5},
                'eol_sep': {'type': 'string', 'required': False, 'default': '\n'},
                'json_format': {'type': 'boolean', 'required': False, 'default': False}
            }
        }
}
