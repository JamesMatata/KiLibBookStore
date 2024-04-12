from django.contrib import admin

from orders.models import Order, OrderItem, Book_Lease, LeasedItem

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Book_Lease)
admin.site.register(LeasedItem)
