'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
User interests model mongo based.
---------------------------------------------------
'''

from mongoengine import Document, fields
from helpers.constants import INTERESTS



class Interest(Document):
    user_id = fields.IntField(required=True)
    tags = fields.ListField(field=fields.StringField(choices=INTERESTS))

    meta = {
        'collection': 'interests',
        'indexes': [
            {'fields': ['user_id'], 'unique': True},
            {'fields': ['tags']},
        ],
    }
