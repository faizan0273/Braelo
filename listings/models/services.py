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

from ..helpers.constants import (
    ECO_FRIENDLY_PRODUCTS,
    SAME_DAY_SERVICE,
    AVAILABLE_VEHICLES,
    REGULAR_MAINTENANCE,
    SEASONAL_SERVICES,
    SERVICE_AVAILABLE,
    PERSONALISED_FITNESS_PLAN,
    GROUP_SESSION,
    FREE_APPOINTMENTS,
    EVENT_TYPES,
    CUSTOMIZABLE_PACKAGE,
    PACKING_MATERIALS,
    GOODS_TRANSIT_INSURANCE,
    DELIVERY_AVAILABILITY,
    ORGANIC_SOURCED,
    REGULAR_DELIVERY_OPTION,
    DIFFERENT_PACKAGES,
    RECURRING_SERVICE_PLAN,
    FURNITURE_SELECTION,
    RENDERING_VISUALIZING,
    HOMEMADE_SERVICE,
    MENU_CUSTOMIZATION,
    NEGOTIABLE,
    PAYMENT_OPTION
)


class ServicesListing(Document):
    '''
    Service category listings.
    '''

    category = fields.StringField(required=True)
    subcategory = fields.StringField(required=True)
    pictures = fields.ListField(fields.ImageField(), required=False)
    title = fields.StringField(required=True)
    description = fields.StringField(required=True)
    location = fields.StringField(required=True)

    # category based
    service_type = fields.StringField(required=True)
    availability = fields.IntField(required=True)
    pricing_structure = fields.IntField(required=True)
    service_area = fields.StringField(required=True)
    cleaning_type = fields.StringField(required=False)
    insurance = fields.FloatField(required=False)
    payment_options = fields.StringField(choices=PAYMENT_OPTION,required=True)
    offered_services = fields.StringField(
        max_length=4, required=False, default=None
    )
    eco_friendly_product = fields.StringField(
        choices=ECO_FRIENDLY_PRODUCTS, max_length=2, default=None
    )
    provided_equipment = fields.StringField(
        max_length=2, required=False, default=None
    )
    price = fields.DecimalField(required=True)
    certifications = fields.StringField(
        max_length=2, required=False, default=None
    )
    negotiable = fields.StringField(choices=NEGOTIABLE,required=False)
    # Extra fields as per different subcategories
    # Handy man
    experience_qualifications = fields.StringField(required=False)
    other = fields.StringField(required=False)
    same_day_service = fields.StringField(
        choices=SAME_DAY_SERVICE, required=False
    )
    # Driver
    insurance_bonding_status = fields.StringField(required=False)
    additional_service = fields.StringField(required=False)
    vehicle_type = fields.StringField(
        choices=AVAILABLE_VEHICLES, required=False
    )
    # Landscaping
    regular_maintenance = fields.StringField(
        choices=REGULAR_MAINTENANCE, required=False
    )
    seasonal_service = fields.StringField(
        choices=SEASONAL_SERVICES, required=False
    )
    # Consultancy
    initial_consultation = fields.StringField(
        choices=SERVICE_AVAILABLE, required=False
    )
    # Home automation
    supported_products = fields.StringField(required=False)
    # Classes and courses
    subject_skills = fields.StringField(required=False)
    class_duration = fields.IntField(required=False)
    # Personal training
    session_format = fields.StringField(
        choices=SERVICE_AVAILABLE, required=False
    )
    personalised_fitness_plan = fields.StringField(
        choices=PERSONALISED_FITNESS_PLAN, required=False
    )
    group_session = fields.StringField(choices=GROUP_SESSION, required=False)
    # Immigration and visa
    free_appointment = fields.StringField(
        choices=FREE_APPOINTMENTS, required=False
    )
    # Event services
    portfolio = fields.StringField(required=False)
    event_type = fields.StringField(choices=EVENT_TYPES, required=False)
    customizable_package = fields.StringField(
        choices=CUSTOMIZABLE_PACKAGE, required=False
    )
    # Movers and packers
    packing_material = fields.StringField(
        choices=PACKING_MATERIALS, required=False
    )
    insurance_for_goods = fields.StringField(
        choices=GOODS_TRANSIT_INSURANCE, required=False
    )
    # Farm and fresh
    delivery_availability = fields.StringField(
        choices=DELIVERY_AVAILABILITY, required=False
    )
    organic_sourced = fields.StringField(
        choices=ORGANIC_SOURCED, required=False
    )
    regular_delivery_option = fields.StringField(
        choices=REGULAR_DELIVERY_OPTION, required=False
    )
    # Video and photography
    different_packages = fields.StringField(
        choices=DIFFERENT_PACKAGES, required=False
    )
    recurring_services = fields.StringField(
        choices=RECURRING_SERVICE_PLAN, required=False
    )
    # interior design
    material_furniture_Selection = fields.StringField(
        choices=FURNITURE_SELECTION, required=False
    )
    rendering_visualizations = fields.StringField(
        choices=RENDERING_VISUALIZING, required=False
    )
    # Homemade food
    service_availability = fields.StringField(
        choices=HOMEMADE_SERVICE, required=False
    )
    # Catering
    cuisine_type = fields.StringField(required=False)
    # Influencer
    platform = fields.StringField(required=False)
    audience_size = fields.IntField(required=False)
    # Ac Services
    # todo check if specialization in personal training field also handle in this
    brands_specialization = fields.StringField(required=False)
    # cake
    cake_type = fields.StringField(required=False)
    # finger food
    menu = fields.StringField(required=False)
    # buffet
    menu_customization = fields.StringField(
        choices=MENU_CUSTOMIZATION, required=False
    )
    # Transport service
    distance = fields.StringField(required=False)

    # Timestamps
    created_at = fields.DateTimeField(default=timezone.now())
    updated_at = fields.DateTimeField(default=timezone.now())

    meta = {
        'collection': 'services_listing',
        'ordering': ['-created_at'],
        'indexes': [
            {'fields': ['title']},
            {'fields': ['location']},
            {'fields': ['category']},
            {'fields': ['subcategory']},
        ],
    }
