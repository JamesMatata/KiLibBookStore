from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('process/', views.process_payment, name='process_payment'),
    path('callback/', views.LNMCallbackUrlAPIView.as_view(), name='callback'),
    path('confirmPurchase/<int:id>', views.confirmPurchase, name='confirmPurchase'),
    path('confirmLease/<int:id>', views.confirmLease, name='confirmLease'),
]
