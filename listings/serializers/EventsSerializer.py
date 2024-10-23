"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for Event Listings based endpoints
---------------------------------------------------
"""

from listings.serializers.ParentSerializer import Serializer
from listings.models import EventsListing


class EventsSerializer(Serializer):
    class Meta:
        model = EventsListing
        fields = "__all__"
        category = "events"
