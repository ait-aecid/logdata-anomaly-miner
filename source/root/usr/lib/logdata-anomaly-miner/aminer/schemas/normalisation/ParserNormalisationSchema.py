# skipcq: PYL-W0104
{
    'Parser': {
        'required': True,
        'type': 'list',
        'has_start': True,
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'type': 'string', 'required': True},
                'start': {'type': 'boolean'},
                'type': {'type': 'parsermodel', 'coerce': 'toparsermodel', 'required': True},
                'name': {'type': 'string', 'required': True},
                'args': {'type': ['string', 'list'], 'schema': {'type': ['string', 'integer']}, 'nullable': True},
                'branch_model_dict': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'id': {
                    'type': ['boolean', 'float', 'integer', 'string']}, 'model': {'type': 'string'}}}},
                'date_formats': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'format': {'type': 'list', 'schema': {
                    'type': 'string', 'nullable': True}}}}},
                'value_sign_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory'], 'default': 'none'},
                'value_pad_type': {'type': 'string', 'allowed': ['none', 'zero', 'blank'], 'default': 'none'},
                'exponent_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory'], 'default': 'none'},
                'start_year': {'type': 'integer', 'nullable': True, 'default': None},
                'delimiter': {'type': 'string'},
                'escape': {'type': 'string', 'nullable': True, 'default': None},
                'consume_delimiter': {'type': 'boolean', 'default': False},
                'key_parser_dict': {'type': 'dict'},
                'optional_key_identifier': {'type': 'string', 'default': 'optional_key_'}
            }
        }
    },
}
