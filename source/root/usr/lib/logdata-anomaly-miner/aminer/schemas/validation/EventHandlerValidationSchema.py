# skipcq: PYL-W0104
{
    'EventHandlers': {
        'required': False,
        'type': 'list',
        'nullable': True,
        'default': None,
        'schema': {
            'type': 'dict',
            'allow_unknown': False,
            'oneof_schema': [
                {
                    'id': {'type': 'string', 'required': True},
                    'type': {'type': 'string', 'forbidden': [
                        'KafkaEventHandler', 'StreamPrinterEventHandler', 'SyslogWriterEventHandler'], 'required': True},
                    'json': {'type': 'boolean', 'default': False}
                },
                {
                    'id': {'type': 'string', 'required': True},
                    'type': {'type': 'string', 'allowed': ['KafkaEventHandler'], 'required': True},
                    'json': {'type': 'boolean', 'default': False},
                    'topic': {'type': 'string', 'required': True},
                    'cfgfile': {'type': 'string', 'default': '/etc/aminer/kafka-client.conf'},
                    'options': {'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': ['string', 'list', 'integer']}}},
                },
                {
                    'id': {'type': 'string', 'required': True},
                    'type': {'type': 'string', 'allowed': ['StreamPrinterEventHandler'], 'required': True},
                    'json': {'type': 'boolean', 'default': False},
                    'output_file_path': {'type': 'string'}
                },
                {
                    'id': {'type': 'string', 'required': True},
                    'type': {'type': 'string', 'allowed': ['SyslogWriterEventHandler'], 'required': True},
                    'json': {'type': 'boolean', 'default': False},
                    'instance_name': {'type': 'string', 'default': 'aminer'}
                }
            ]
        }
    }
}
