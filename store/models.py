# from django.conf import settings
# from django.db import models

from django.db import models
from django.urls import reverse

from django.contrib.auth import get_user_model
User = get_user_model()


class ProductManager(models.Manager):
    def get_queryset(self):
        return super(ProductManager, self).get_queryset().filter(is_active=True)


class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255, unique=True)

    class Meta:
        verbose_name_plural = 'categories'

    def get_absolute_url(self):
        return reverse('store:category_list', args=[self.slug])

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, blank=True, null=True, related_name='product', on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_creator')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, default='admin')
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='images/', default='book_files/default.png')
    slug = models.SlugField(max_length=255, unique=True)
    price = models.IntegerField()
    book_lease_rates = models.IntegerField()
    in_stock = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    objects = models.Manager()
    products = ProductManager()

    class Meta:
        verbose_name_plural = 'Products'
        ordering = ('-created',)

    users_wishlist = models.ManyToManyField(User, related_name="user_wishlist", blank=True)

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    def __str__(self):
        return self.title


class County(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class CountyDeliveryCharge(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='delivery_charges')
    door_delivery_charge = models.DecimalField(max_digits=10, decimal_places=2)
    pickup_point_charge = models.DecimalField(max_digits=10, decimal_places=2)
    in_store_pickup_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.county.name} - Delivery Charges'

