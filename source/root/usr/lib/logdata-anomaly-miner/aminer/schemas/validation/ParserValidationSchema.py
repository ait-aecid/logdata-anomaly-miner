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
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'empty': False, 'forbidden': [
                        'ElementValueBranchModelElement', 'DecimalIntegerValueModelElement', 'DecimalFloatValueModelElement',
                        'MultiLocaleDateTimeModelElement', 'DelimitedDataModelElement', 'JsonModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True, 'empty': False},
                    'args': {'type': ['string', 'list'], 'schema': {'type': ['string', 'integer']}}
                },
                {
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['ElementValueBranchModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True, 'empty': False},
                    'args': {'type': ['string', 'list'], 'schema': {'type': ['string', 'integer']}, 'required': True},
                    'branch_model_dict': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'id': {'type': [
                        'boolean', 'float', 'integer', 'string']}, 'model': {'type': 'string', 'empty': False}}}, 'required': True}
                },
                {
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['DecimalFloatValueModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True},
                    'value_sign_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory']},
                    'value_pad_type': {'type': 'string', 'allowed': ['none', 'zero', 'blank']},
                    'exponent_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory']}
                },
                {
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['DecimalIntegerValueModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True, 'empty': False},
                    'value_sign_type': {'type': 'string', 'allowed': ['none', 'optional', 'mandatory']},
                    'value_pad_type': {'type': 'string', 'allowed': ['none', 'zero', 'blank']}
                },
                {
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['MultiLocaleDateTimeModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True, 'empty': False},
                    'date_formats': {'type': 'list', 'schema': {'type': 'dict', 'schema': {'format': {'type': 'list', 'schema': {
                        'type': 'string', 'nullable': True, 'empty': False}, 'maxlength': 3, 'minlength': 3}}}, 'required': True},
                    'start_year': {'type': 'integer', 'nullable': True}
                },
                {
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['DelimitedDataModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True, 'empty': False},
                    'delimiter': {'type': 'string', 'required': True, 'empty': False},
                    'escape': {'type': 'string'},
                    'consume_delimiter': {'type': 'boolean'}
                },
                {
                    'id': {'type': 'string', 'required': True, 'empty': False},
                    'start': {'type': 'boolean'},
                    'type': {'type': 'string', 'allowed': ['JsonModelElement'], 'required': True},
                    'name': {'type': 'string', 'required': True, 'empty': False},
                    'key_parser_dict': {'type': 'dict', 'required': True},
                    'optional_key_prefix': {'type': 'string'}
                },
            ]
        }
    }
}
