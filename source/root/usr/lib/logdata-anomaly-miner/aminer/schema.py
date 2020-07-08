# This schema validates the config-files in yaml-format

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

# skipcq: PYL-W0104
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
        'Core.PersistenceDir' : {
            'required' : False,
            'type': 'string',
            'default': '/var/lib/aminer'
        },
        'MailAlerting.TargetAddress' : {
            'required' : False,
            'type': 'string'
        },
        'MailAlerting.FromAddress' : {
            'required' : False,
            'type': 'string'
        },
        'MailAlerting.SubjectPrefix' : {
            'required' : False,
            'type': 'string',
            'default': 'AMiner Alerts:'
        },
        'MailAlerting.AlertGraceTime' : {
            'required' : False,
            'type': 'integer',
            'default': 0
        },
        'MailAlerting.EventCollectTime' : {
            'required' : False,
            'type': 'integer',
            'default': 10
        },
        'MailAlerting.MinAlertGap' : {
            'required' : False,
            'type': 'integer',
            'default': 600
        },
        'MailAlerting.MaxAlertGap' : {
            'required' : False,
            'type': 'integer',
            'default': 600
        },
        'MailAlerting.MaxEventsPerMessage' : {
            'required' : False,
            'type': 'integer',
            'default': 1000
        },
        'LogPrefix' : {
            'required' : False,
            'type': 'string',
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
                'Verbose': {'type': 'boolean', 'required': False, 'default': False},
                'MultiSource': {'type': 'boolean', 'required': False, 'default': False},
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
                    'type' : {'type': 'string', 'allowed': ['StreamPrinterEventHandler','SyslogWriterEventHandler']},
                    'json' : {'type': 'boolean', 'required': False, 'default': False},
                    'args' : {'type': ['string','list'], 'schema': {'type': 'string'}}
                }
            }
        }
}

