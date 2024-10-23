"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Faizan
---------------------------------------------------

Description:
Serializer file for Unsave Listings based endpoints
---------------------------------------------------
"""

from bson import ObjectId
from rest_framework import serializers as drf_serializers


class UnsaveItemSerializer(drf_serializers.Serializer):
    listing_id = drf_serializers.CharField(required=True)

    def validate_listing_id(self, listing_id):
        return ObjectId(listing_id)
