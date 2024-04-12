from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Seller, CustomUser

admin.site.register(CustomUser),
admin.site.register(Seller),
