'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
admin file.
---------------------------------------------------
'''

from django.contrib import admin
from .models import User

# Register your models here.
admin.site.register(User)
