from mongoengine import Document
from mongoengine.fields import (
    IntField,
    StringField,
    DateTimeField,
)


class Review(Document):
    user_id = IntField()
    review = StringField(required=True)
    created_at = DateTimeField()

    meta = {'collection': 'braelo_reviews'}
