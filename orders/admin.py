from django.contrib import admin

from orders.models import Order, OrderItem, BookLease, LeasedItem

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(BookLease)
admin.site.register(LeasedItem)
