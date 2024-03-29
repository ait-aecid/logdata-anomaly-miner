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
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'type': {'type': 'string', 'forbidden': [
                        'KafkaEventHandler', 'ZmqEventHandler', 'StreamPrinterEventHandler', 'SyslogWriterEventHandler'], 'required': True},
                    'json': {'type': 'boolean'},
                    'score': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'type': {'type': 'string', 'allowed': ['ZmqEventHandler'], 'required': True},
                    'json': {'type': 'boolean'},
                    'pretty': {'type': 'boolean'},
                    'score': {'type': 'boolean'},
                    'weights': {'type': 'dict', 'nullable': True},
                    'auto_weights': {'type': 'boolean'},
                    'auto_weights_history_length': {'type': 'integer', 'default': 1000, 'min': 1},
                    'topic': {'type': 'string', 'required': False},
                    'url': {'type': 'string', 'empty': False},
                },
                {
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'type': {'type': 'string', 'allowed': ['KafkaEventHandler'], 'required': True},
                    'json': {'type': 'boolean'},
                    'pretty': {'type': 'boolean'},
                    'score': {'type': 'boolean'},
                    'weights': {'type': 'dict', 'nullable': True},
                    'auto_weights': {'type': 'boolean'},
                    'auto_weights_history_length': {'type': 'integer', 'default': 1000, 'min': 1},
                    'topic': {'type': 'string', 'required': True, 'empty': False},
                    'cfgfile': {'type': 'string', 'empty': False},
                    'options': {'type': 'dict', 'schema': {
                        'id': {'type': 'string', 'empty': False}, 'type': {'type': ['string', 'list', 'integer']}}},
                },
                {
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'type': {'type': 'string', 'allowed': ['StreamPrinterEventHandler'], 'required': True},
                    'json': {'type': 'boolean'},
                    'pretty': {'type': 'boolean'},
                    'score': {'type': 'boolean'},
                    'weights': {'type': 'dict', 'nullable': True},
                    'auto_weights': {'type': 'boolean'},
                    'auto_weights_history_length': {'type': 'integer', 'default': 1000, 'min': 1},
                    'output_file_path': {'type': 'string', 'empty': False}
                },
                {
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'type': {'type': 'string', 'allowed': ['SyslogWriterEventHandler'], 'required': True},
                    'json': {'type': 'boolean'},
                    'pretty': {'type': 'boolean'},
                    'score': {'type': 'boolean'},
                    'weights': {'type': 'dict', 'nullable': True},
                    'auto_weights': {'type': 'boolean'},
                    'auto_weights_history_length': {'type': 'integer', 'default': 1000, 'min': 1},
                    'instance_name': {'type': 'string', 'default': 'aminer', 'empty': False}
                }
            ]
        }
    }
}
