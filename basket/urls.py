from django.urls import path
from .views import BasketSummaryView, BasketAddView, BasketDeleteView, BasketUpdateView, GetDeliveryCostView

app_name = 'basket'

urlpatterns = [
    path('', BasketSummaryView.as_view(), name='basket_summary'),
    path('add/', BasketAddView.as_view(), name='basket_add'),
    path('delete/', BasketDeleteView.as_view(), name='basket_delete'),
    path('update/', BasketUpdateView.as_view(), name='basket_update'),
    path('get_delivery_cost/', GetDeliveryCostView.as_view(), name='get_delivery_cost'),
]
