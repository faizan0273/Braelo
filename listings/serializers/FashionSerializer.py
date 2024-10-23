"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for fashion Listings based endpoints
---------------------------------------------------
"""

from listings.serializers.ParentSerializer import Serializer
from listings.models import FashionListing


class FashionSerializer(Serializer):
    class Meta:
        model = FashionListing
        fields = "__all__"
        category = "fashion"
