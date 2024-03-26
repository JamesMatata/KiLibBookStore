from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('purchase/', views.pay, name='pay'),
    path('callback/', views.LNMCallbackUrlAPIView.as_view(), name='callback'),
    path('confirmPurchase/<int:id>', views.confirmPurchase, name='confirmPurchase'),
    path('lease/', views.leaseBook, name='lease'),
    path('confirmLease/<int:id>', views.confirmLease, name='confirmLease'),
]
