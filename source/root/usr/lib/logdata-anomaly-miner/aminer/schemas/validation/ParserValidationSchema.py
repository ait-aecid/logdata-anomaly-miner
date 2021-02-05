# skipcq: PYL-W0104
{
    'Parser': {
        'required': True,
        'type': 'list',
        'schema': {
            'type': 'dict',
            'allow_unknown': False,
            'oneof_schema': [
                {
                    'id': {'type': 'string'},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'forbidden': [
                        'ElementValueBranchModelElement', 'DecimalIntegerValueModelElement', 'DecimalIntegerValueModelElement',
                        'MultiLocaleDateTimeModelElement']},
                    'name': {'type': 'string'},
                    'args': {'type': ['string', 'list'], 'schema': {'type': ['string', 'integer']}}
                },
                {
                    'id': {'type': 'string'},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['ElementValueBranchModelElement']},
                    'name': {'type': 'string'},
                    'args': {'type': ['string', 'list'], 'schema': {'type': ['string', 'integer']}},
                    'branch_model_dict': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'id': {
                         'type': ['boolean', 'float', 'integer', 'string']}, 'model': {'type': 'string'}}}},
                },
                {
                    'id': {'type': 'string'},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['DecimalFloatValueModelElement']},
                    'name': {'type': 'string'},
                    'value_sign_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory'], 'default': 'none'},
                    'value_pad_type': {'type': 'string', 'allowed': ['none', 'zero', 'blank'], 'default': 'none'},
                    'exponent_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory'], 'default': 'none'}
                },
                {
                    'id': {'type': 'string'},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['DecimalIntegerValueModelElement']},
                    'name': {'type': 'string'},
                    'value_sign_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory'], 'default': 'none'},
                    'value_pad_type': {'type': 'string', 'allowed': ['none', 'zero', 'blank'], 'default': 'none'}
                },
                {
                    'id': {'type': 'string'},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['MultiLocaleDateTimeModelElement']},
                    'name': {'type': 'string'},
                    'date_formats': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'format': {'type': 'list', 'schema': {
                        'type': 'string', 'nullable': True}, 'maxlength': 3, 'minlength': 3}}}},
                }
            ]
        }
    }
}
