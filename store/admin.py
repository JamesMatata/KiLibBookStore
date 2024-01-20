from django.contrib import admin
from store.models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # Displaying things in a specific way in the admin area
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    # slug field will get populated automatically according to what is types on the name


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'slug', 'price',
                    'in_stock', 'created', 'is_active']

    list_filter = ['in_stock', 'is_active']
    list_editable = ['price', 'in_stock']
    prepopulated_fields = {'slug': ('title',)}
