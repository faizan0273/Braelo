"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for real estate Listings based endpoints
---------------------------------------------------
"""

from listings.serializers.ParentSerializer import Serializer
from listings.models import RealEstateListing


class RealEstateSerializer(Serializer):
    class Meta:
        model = RealEstateListing
        category = "real estate"
        fields = "__all__"
