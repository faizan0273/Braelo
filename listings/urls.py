'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
End points registry file.
---------------------------------------------------
'''

from django.urls import path

from Braeloo.listings.api.category import Categories

urlpatterns = [
    path('meta', Categories.as_view(), name='categories-list'),
]
