from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager


# Create your models here.


class CustomUserManager(BaseUserManager):
    '''
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    '''

    def create_user(self, username, **extra_fields):
        '''
        Create and save a User with the given email and password.
        '''
        if not username:
            raise ValueError('The Email must be set')
        uname = self.normalize_email(username)
        user = self.model(username=uname, **extra_fields)
        if 'password' in extra_fields:
            user.set_password(extra_fields['password'])
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        '''
        Create and save a SuperUser with the given email and password.
        '''
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    USER_ROLES = (
        ('Admin', 'Admin'),
        ('Client', 'Client'),
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
    # New field for storing OTP
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(auto_now=True)
    username = models.CharField(
        max_length=255,
        verbose_name='username',
        unique=True,
        default='temp_username',
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return f'{self.id}: {self.username}'
