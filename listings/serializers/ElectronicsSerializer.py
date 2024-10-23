"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for electronics Listings based endpoints
---------------------------------------------------
"""

from listings.serializers.ParentSerializer import Serializer
from listings.models import ElectronicsListing


class ElectronicsSerializer(Serializer):
    class Meta:
        model = ElectronicsListing
        fields = "__all__"
        category = "electronics"
