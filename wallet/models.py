from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet_owner')
    balance = models.IntegerField(default=0)
    amount_locked = models.IntegerField(default=0)
    usable_amount = models.IntegerField(default=0)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Wallets'
        ordering = ('-updated_on',)

    def save(self, *args, **kwargs):
        if self.amount_locked:
            self.usable_amount = self.balance-self.amount_locked
        else:
            self.usable_amount = self.balance
        super(Wallet, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.user)
