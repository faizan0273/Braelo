'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Listing model mongo based.
---------------------------------------------------
'''

from datetime import datetime
from mongoengine import Document, fields


class Listing(Document):
    category = fields.ReferenceField('Category', required=True)
    subcategory = fields.ReferenceField('subcategory', required=True)
    # Reference to Subcategory model
    # Reference to Category model
    picture = fields.ImageField(required=False)  # Optional field for image
    ad_title = fields.StringField(required=True)  # Ad title is mandatory
    description = fields.StringField(required=True)  # Description is mandatory
    location = fields.StringField(required=False)  # Optional field for location
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'listings',
        'ordering': ['-created_at'],  # Order by newest first
        'indexes': [
            {'fields': ['category']},  # Index for category field
        ],
    }

    def save(self, *args, **kwargs):
        """Override the save method to update the updated_at field"""
        self.updated_at = datetime.utcnow()
        return super(Listing, self).save(*args, **kwargs)

    def __str__(self):
        return self.ad_title
