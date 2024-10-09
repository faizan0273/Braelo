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
from ..helpers.constants.jobs import JobsConstants

class JobsListing(Document):
    '''
    Jobs category listings.
    '''

    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(fields.ImageField(), required=False)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    location = fields.StringField(required=True)

    # category based
    job_tittle = fields.StringField(required=True)
    required_skills = fields.StringField(required=True)
    experience_level = fields.StringField(required=True)
    employment_type = fields.StringField(required=True)
    working_hours = fields.IntField(required=False)
    benefits_offered = fields.StringField(required=False)
    work_permit = fields.StringField(choices=JobsConstants.WORK_PERMIT, required=True)
    salary_range = fields.StringField(required=True)
    negotiable = fields.StringField(choices=JobsConstants.NEGOTIABLE, required=True)

    # Part-time
    flexibility = fields.IntField(required=False)

    # freelancer
    project_type = fields.StringField(required=False)
    contract_duration = fields.IntField(required=False)

    # Home offices
    remote_work_tools = fields.StringField(required=False)
    passenger_capacity = fields.IntField(required=False)

    # Helper
    service_type = fields.StringField(required=False)
    duties = fields.StringField(required=False)
    accommodation_provided = fields.StringField(required=False)
    own_tools = fields.StringField(choices=JobsConstants.HELPER_TOOLS, required=False)
    car_needed = fields.StringField(choices=JobsConstants.HELPER_CAR, required=False)
    helper_pay = fields.StringField(choices=JobsConstants.HELPER_PAY, required=False)

    # Timestamps
    created_at = fields.DateTimeField(default=timezone.now())
    updated_at = fields.DateTimeField(default=timezone.now())

    meta = {
        'collection': 'jobs_listing',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['title']},
            {'fields': ['location']},
            {'fields': ['category']},
            {'fields': ['subcategory']},
        ],
    }
