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
                'id': {'type': 'string'},
                'type': {'type': 'eventhandlertype', 'coerce': 'toeventhandlertype'},
                'json': {'type': 'boolean', 'required': False, 'default': False},
                'instance_name': {'type': 'string', 'required': False, 'default': 'aminer'},
                'topic': {'type': 'string'},
                'cfgfile': {'type': 'string'},
                'options': {'type': 'dict', 'schema': {'id': {'type': 'string'}, 'type': {'type': ['string', 'list', 'integer']}}},
                'output_file_path': {'type': 'string', 'required': False}
            }
        }
    }
}
