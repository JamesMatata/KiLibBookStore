import datetime

from django.conf import settings
from django.db import models
from django.utils import timezone

from store.models import Product


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orderer')
    full_name = models.CharField(max_length=50)
    county = models.CharField(max_length=100)
    deliveryPoint = models.CharField(max_length=150)
    deliveryPoint2 = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_paid = models.IntegerField()
    receipt_No = models.CharField(max_length=200, blank=True)
    billing_status = models.BooleanField(default=False)
    email = models.CharField(max_length=150, blank=True)
    delivered = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.created)


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              related_name='items',
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                related_name='order_items',
                                on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)


class Book_Lease(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leased')
    full_name = models.CharField(max_length=50)
    county = models.CharField(max_length=100)
    deliveryPoint = models.CharField(max_length=150)
    deliveryPoint2 = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    total_paid = models.IntegerField()
    receipt_No = models.CharField(max_length=200, blank=True)
    billing_status = models.BooleanField(default=False)
    leased_weeks = models.IntegerField(default=0)
    return_date = models.DateField(null=True, blank=True)
    return_status = models.BooleanField(default=False)
    purchase_cost = models.IntegerField()
    email = models.CharField(max_length=150, blank=True)
    delivered = models.BooleanField(default=False)
    delivered_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ('-created',)

    def save(self, *args, **kwargs):
        if self.delivered and not self.delivered_date:
            self.delivered_date = timezone.now()
        if self.delivered_date is not None:
            self.return_date = self.delivered_date + datetime.timedelta(weeks=self.leased_weeks)
        super(Book_Lease, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.created)


class LeasedItem(models.Model):
    Book_Lease = models.ForeignKey(Book_Lease,
                                   related_name='lease',
                                   on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                related_name='leased_items',
                                on_delete=models.CASCADE)
    lease_rate = models.IntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)
