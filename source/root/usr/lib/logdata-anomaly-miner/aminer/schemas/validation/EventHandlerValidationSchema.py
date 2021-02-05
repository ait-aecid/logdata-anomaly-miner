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
                    'id': {'type': 'string'},
                    'type': {'type': 'string', 'forbidden': ['KafkaEventHandler', 'StreamPrinterEventHandler']},
                    'json': {
                        'type': 'boolean',
                        'required': False,
                        'default': False
                    }
                },
                {
                    'id': {'type': 'string'},
                    'type': {'type': 'string', 'allowed': ['KafkaEventHandler']},
                    'json': {
                        'type': 'boolean',
                        'required': False,
                        'default': False
                    },
                    'topic': {'type': 'string'},
                    'cfgfile': {'type': 'string'},
                    'options': {'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': ['string', 'list', 'integer']}}},
                },
                {
                    'id': {'type': 'string'},
                    'type': {'type': 'string', 'allowed': ['StreamPrinterEventHandler']},
                    'json': {
                        'type': 'boolean',
                        'required': False,
                        'default': False
                    },
                    'output_file_path': {'type': 'string', 'required': False}
                },
                {
                    'id': {'type': 'string'},
                    'type': {'type': 'string', 'forbidden': ['KafkaEventHandler', 'StreamPrinterEventHandler']},
                    'json': {
                        'type': 'boolean',
                        'required': False,
                        'default': False
                    },
                    'instance_name': {'type': 'string', 'required': False, 'default': 'aminer'}
                }
            ]
        }
    }
}
