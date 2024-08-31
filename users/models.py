from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        print("user created")
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    USER_ROLES = (
        ("Admin", "Admin"),
        ("Client", "Client"),
    )

    email = models.EmailField(null=True, blank=True)
    password = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    google_id = models.CharField(max_length=255, null=True, blank=True)
    apple_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=255, choices=USER_ROLES)

    objects = UserManager()

    USERNAME_FIELD = 'phone'

    # REQUIRED_FIELDS = ['phone_number', 'name', 'first_name', 'last_name']

    def __str__(self):
        return self.email
