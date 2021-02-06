# skipcq: PYL-W0104
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
                'instance_name': {'type': 'string', 'default': 'aminer'},
                'topic': {'type': 'string'},
                'cfgfile': {'type': 'string', 'default': '/etc/aminer/kafka-client.conf'},
                'options': {'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': ['string', 'list', 'integer']}}},
                'output_file_path': {'type': 'string'}
            }
        }
    }
}
