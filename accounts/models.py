from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    # is_admin=models.BooleanField('Is Admin',default=False)
    is_student = models.BooleanField('student status', default=False)
    is_teacher = models.BooleanField('teacher status', default=False)
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Seller(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    business_name = models.CharField(max_length=200, unique=False)
    business_email = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.business_name
