from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    is_admin = models.BooleanField('Is Admin', default=False)
    is_seller = models.BooleanField('Seller status', default=False)
    is_buyer = models.BooleanField('Buyer status', default=False)
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email',)

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Seller(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    business_name = models.CharField(max_length=200, unique=False)
    business_email = models.CharField(max_length=200, unique=True)
    business_address = models.CharField(max_length=200, unique=False)

    def __str__(self):
        return self.business_name


