"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for vehicle Listings based endpoints
---------------------------------------------------
"""

from listings.serializers.ParentSerializer import Serializer
from listings.models import VehicleListing


class VehicleSerializer(Serializer):
    class Meta:
        model = VehicleListing
        fields = "__all__"
        category = "vehicles"
