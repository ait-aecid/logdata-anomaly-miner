{
    'EventHandlers': {
        'required': False,
        'type': 'list',
        'nullable': True,
        'default': None,
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'type': 'string', 'required': True},
                'type': {'type': 'eventhandlertype', 'coerce': 'toeventhandlertype', 'required': True},
                'json': {'type': 'boolean', 'default': False},
                'score': {'type': 'boolean', 'default': False},
                'instance_name': {'type': 'string', 'default': 'aminer'},
                'topic': {'type': 'string'},
                'url': {'type': 'string', 'default': 'ipc:///tmp/aminer'},
                'cfgfile': {'type': 'string', 'default': '/etc/aminer/kafka-client.conf'},
                'options': {'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': ['string', 'list', 'integer']}}},
                'output_file_path': {'type': 'string'},
                'pretty': {'type': 'boolean', 'default': True},
                'weights': {'type': 'dict', 'nullable': True, 'default': None},
                'auto_weights': {'type': 'boolean', 'default': False},
                'auto_weights_history_length': {'type': 'integer', 'default': 1000, 'min': 1}
            }
        }
    }
}
