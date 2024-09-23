from django.contrib import admin

from wallet.models import Wallet


@admin.register(Wallet)
class Wallet(admin.ModelAdmin):
    list_display = ['user', 'balance', 'amount_locked']
