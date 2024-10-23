"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for furniture Listings based endpoints
---------------------------------------------------
"""

from listings.serializers.ParentSerializer import Serializer
from listings.models import FurnitureListing


class FurnitureSerializer(Serializer):
    class Meta:
        model = FurnitureListing
        fields = "__all__"
        category = "furniture"
