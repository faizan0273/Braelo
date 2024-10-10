'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Vehicle Listing model mongo based.
---------------------------------------------------
'''

from django.utils import timezone
from mongoengine import fields, Document
from ..helpers.constants import EventConstants


class EventsListing(Document):
    '''
    Events category listings.
    '''

    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(fields.ImageField(), required=False)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    location = fields.StringField(required=True)

    # category based
    event_type = fields.StringField(required=True)
    event_date = fields.StringField(required=True)
    expected_audience = fields.IntField(required=True)
    special_feature = fields.StringField(required=True)
    industry_focus = fields.IntField(required=False)
    speaker_list = fields.FloatField(required=False)
    ticket_price = fields.DecimalField(required=True)
    negotiable = fields.StringField(
        choices=EventConstants.NEGOTIABLE, required=True
    )
    # Concert
    performer = fields.IntField(required=False)
    genre = fields.StringField(required=False)
    # festivals
    no_of_days = fields.IntField(required=False)
    theme = fields.IntField(required=False)
    major_attraction = fields.StringField(required=False)

    # Timestamps
    created_at = fields.DateTimeField(default=timezone.now())
    updated_at = fields.DateTimeField(default=timezone.now())

    meta = {
        'collection': 'events_listing',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['title']},
            {'fields': ['location']},
            {'fields': ['category']},
            {'fields': ['subcategory']},
        ],
    }
