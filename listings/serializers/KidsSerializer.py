"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for kids Listings based endpoints
---------------------------------------------------
"""

from listings.serializers.ParentSerializer import Serializer
from listings.models import KidsListing


class KidsSerializer(Serializer):
    class Meta:
        model = KidsListing
        fields = "__all__"
        category = "kids"
