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
                    'id': {'type': 'string', 'required': True},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'forbidden': [
                        'ElementValueBranchModelElement', 'DecimalIntegerValueModelElement', 'DecimalIntegerValueModelElement',
                        'MultiLocaleDateTimeModelElement', 'DelimitedDataModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True},
                    'args': {'type': ['string', 'list'], 'schema': {'type': ['string', 'integer']}}
                },
                {
                    'id': {'type': 'string', 'required': True},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['ElementValueBranchModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True},
                    'args': {'type': ['string', 'list'], 'schema': {'type': ['string', 'integer']}, 'required': True},
                    'branch_model_dict': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'id': {
                         'type': ['boolean', 'float', 'integer', 'string']}, 'model': {'type': 'string'}}}, 'required': True}
                },
                {
                    'id': {'type': 'string', 'required': True},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['DecimalFloatValueModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True},
                    'value_sign_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory']},
                    'value_pad_type': {'type': 'string', 'allowed': ['none', 'zero', 'blank']},
                    'exponent_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory']}
                },
                {
                    'id': {'type': 'string', 'required': True},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['DecimalIntegerValueModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True},
                    'value_sign_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory']},
                    'value_pad_type': {'type': 'string', 'allowed': ['none', 'zero', 'blank']}
                },
                {
                    'id': {'type': 'string', 'required': True},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['MultiLocaleDateTimeModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True},
                    'date_formats': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'format': {'type': 'list', 'schema': {
                        'type': 'string', 'nullable': True}, 'maxlength': 3, 'minlength': 3}}}, 'required': True},
                    'start_year': {'type': 'integer', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'required': True},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['DelimitedDataModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True},
                    'delimiter': {'type': 'string', 'required': True},
                    'escape': {'type': 'string'},
                    'consume_delimiter': {'type': 'boolean'}
                },
            ]
        }
    }
}
