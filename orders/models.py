import datetime
from django.conf import settings
from django.db import models
from django.utils import timezone
from store.models import Product


class CommonInfo(models.Model):
    OWNERSHIP_OPTIONS = [
        ('purchase', 'Purchase'),
        ('lease', 'Lease'),
    ]

    DELIVERY_METHODS = [
        ('in-store', 'In-store'),
        ('door-delivery', 'Door Delivery'),
        ('pickup-point', 'pick-up Point'),
    ]

    PAYMENT_METHODS = [
        ('m-pesa', 'M-Pesa'),
        ('wallet', 'Wallet'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=50)
    ownership_option = models.CharField(max_length=100, choices=OWNERSHIP_OPTIONS)
    delivery_method = models.CharField(max_length=100, choices=DELIVERY_METHODS)
    county = models.CharField(max_length=100, blank=True, null=True)
    delivery_point = models.CharField(max_length=150, null=True, blank=True)
    delivery_point2 = models.CharField(max_length=150, null=True, blank=True)
    pickup_point = models.CharField(max_length=150, null=True, blank=True)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHODS)
    mpesa_phone = models.CharField(max_length=15, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    delivery_costs = models.IntegerField(default=0)
    receipt_no = models.CharField(max_length=200, null=True, blank=True)
    total_paid = models.IntegerField()
    billing_status = models.BooleanField(default=False)
    email = models.CharField(max_length=150, null=True, blank=True)
    delivered = models.BooleanField(default=False)
    delivered_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True


class Order(CommonInfo):
    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return f"Order {self.id} - {self.created}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"OrderItem {self.id} - Order {self.order.id}"


class BookLease(CommonInfo):
    leased_weeks = models.IntegerField(default=0)
    return_date = models.DateField(null=True, blank=True)
    return_status = models.BooleanField(default=False)
    purchase_cost = models.IntegerField()

    class Meta:
        ordering = ('-created',)

    def save(self, *args, **kwargs):
        if self.delivered and not self.delivered_date:
            self.delivered_date = timezone.now().date()
        if self.delivered_date:
            self.return_date = self.delivered_date + datetime.timedelta(weeks=self.leased_weeks)
        super(BookLease, self).save(*args, **kwargs)

    def __str__(self):
        return f"BookLease {self.id} - {self.created}"


class LeasedItem(models.Model):
    book_lease = models.ForeignKey(BookLease, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='leased_items', on_delete=models.CASCADE)
    lease_rate = models.IntegerField()
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"LeasedItem {self.id} - Lease {self.book_lease.id}"
