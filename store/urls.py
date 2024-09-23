from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),
    path('item/<slug:slug>/', views.product_detail, name='product_detail'),
    path('shop/<slug:category_slug>/', views.category_list, name='category_list'),
    path('search/', views.searched_items, name='searched_items'),
    path('addProducts/', views.add_product, name='add_product'),
    path('delete_product/<int:id>', views.delete_product, name='delete_product'),
    path('update_product/<int:id>', views.edit_product_details, name='update_product'),
]
