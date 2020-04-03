{
        'LearnMode': {
            'required': False,
            'type': 'boolean'
        },
        'AMinerUser' : {
            'required': False,
            'type': 'string',
            'default': 'aminer'
        },
        'AMinerGroup' : {
            'required': False,
            'type': 'string',
            'default': 'aminer'
        },
        'LogResourceList' : {
            'required' : True,
            'type': 'list',
            'schema': { 'type': 'string' }
        },
        'Parser': {
            'required' : True,
            'type': 'list',
            'schema': {
                'type': 'dict',
                 'schema' : {
                    'id'   : {'type': 'string'},
                    'type' : {'type': 'string'},
                    'name' : {'type': 'string'},
                    'args' : {'type': ['string','list'], 'schema': {'type': 'string'}}
                }
            }
        },
        'Input': {
            'required' : True,
            'type': 'dict',
            'schema': {
                'Verbose': {'type': 'boolean', 'default': 'false'},
                'MultiSource': {'type': 'boolean', 'default': 'false'},
                'TimestampPath': {'type': 'string'}
            }
        },
        'Analysis': {
            'required' : True,
            'type': 'list',
            'schema': {
                'type': 'dict',
                 'schema' : {
                     'id': {'type': 'string', 'required': False, 'default': 'None'},
                     'type' : {'type': 'string', 'allowed': ['NewMatchPathValueDetector','NewMatchPathValueComboDetector']},
                     'paths' : {'type': 'list', 'schema': {'type': 'string'}},
                     'learnMode' : {'type': 'boolean'},
                     'persistence_id' : {'type': 'string', 'required': False, 'default': 'Default'},
                     'output_logline' : {'type': 'boolean', 'required': False, 'default': True},
                     'allow_missing_values' : {'type': 'boolean', 'required': False, 'default': False}
                }
            }
        },
        'EventHandlers': {
            'required' : False,
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'id'   : {'type': 'string'},
                    'type' : {'type': 'string', 'allowed': ['StreamPrinterEventHandler']},
                    'args' : {'type': ['string','list'], 'schema': {'type': 'string'}}
                }
            }
        }
}

