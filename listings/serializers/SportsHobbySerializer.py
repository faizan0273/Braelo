"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for sports_Hobby Listings based endpoints
---------------------------------------------------
"""

from listings.serializers.ParentSerializer import Serializer
from listings.models import SportsHobbyListing


class SportsHobbySerializer(Serializer):
    class Meta:
        model = SportsHobbyListing
        fields = "__all__"
        category = "sports & hobby"
