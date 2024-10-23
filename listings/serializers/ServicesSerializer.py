"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for sevices Listings based endpoints
---------------------------------------------------
"""

from listings.serializers.ParentSerializer import Serializer
from listings.models import ServicesListing


class ServicesSerializer(Serializer):
    class Meta:
        model = ServicesListing
        fields = "__all__"
        category = "events"
