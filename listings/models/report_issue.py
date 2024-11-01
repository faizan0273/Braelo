from mongoengine import Document
from mongoengine.fields import (
    IntField,
    StringField,
    ListField,
    DateTimeField,
    EmailField,
)


class ReportIssue(Document):
    user_id = IntField()
    email = EmailField(required=True)
    subject = StringField(required=True)
    description = StringField(required=True)
    attachments = ListField(required=False, default=None)
    created_at = DateTimeField()

    meta = {
        'collection': 'report_issue',
    }
