"""
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
Serializer file for jobs Listings based endpoints
---------------------------------------------------
"""

from listings.serializers.ParentSerializer import Serializer
from listings.models import JobsListing


class JobsSerializer(Serializer):
    class Meta:
        model = JobsListing
        fields = "__all__"
        category = "jobs"
