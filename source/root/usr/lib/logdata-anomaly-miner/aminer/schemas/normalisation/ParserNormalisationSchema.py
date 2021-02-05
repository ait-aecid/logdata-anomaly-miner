# skipcq: PYL-W0104
{
    'Parser': {
        'required': True,
        'type': 'list',
        'has_start': True,
        'schema': {
            'type': 'dict',
            'schema': {
                'id': {'type': 'string'},
                'start': {'type': 'boolean'},
                'type': {'type': 'parsermodel', 'coerce': 'toparsermodel'},
                'name': {'type': 'string'},
                'args': {'type': ['string', 'list'], 'schema': {'type': ['string', 'integer']}, 'nullable': True},
                'branch_model_dict': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'id': {
                    'type': ['boolean', 'float', 'integer', 'string']}, 'model': {'type': 'string'}}}},
                'date_formats': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'format': {'type': 'list', 'schema': {
                    'type': 'string', 'nullable': True}}}}},
                'value_sign_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory'], 'default': 'none'},
                'value_pad_type': {'type': 'string', 'allowed': ['none', 'zero', 'blank'], 'default': 'none'},
                'exponent_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory'], 'default': 'none'}
            }
        }
    },
}
