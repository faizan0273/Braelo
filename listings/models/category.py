'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Listing categories model mongo based.
---------------------------------------------------
'''

from mongoengine import Document, fields, EmbeddedDocument


class Subcategory(EmbeddedDocument):
    id = fields.ObjectIdField(
        default=lambda: fields.ObjectId(), primary_key=True
    )
    name = fields.StringField(required=True)
    description = fields.StringField()

    def __str__(self):
        return self.name


class Category(Document):
    name = fields.StringField(required=True, unique=True)
    description = fields.StringField()
    subcategories = fields.EmbeddedDocumentListField(Subcategory)

    meta = {
        'collection': 'categories',
        'ordering': ['name'],
        'indexes': [
            {'fields': ['name'], 'unique': True},
        ],
    }

    def __str__(self):
        return self.name
