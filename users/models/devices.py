'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
User device token model.
---------------------------------------------------
'''

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class UserDeviceToken(models.Model):
    PLATFORM_CHOICES = (
        ('android', 'Android'),
        ('ios', 'iOS'),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='device_tokens'
    )
    platform = models.CharField(
        max_length=10, choices=PLATFORM_CHOICES, null=False, blank=False
    )
    token = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self):
        return f"Token for {self.user.email} on {self.platform}"
