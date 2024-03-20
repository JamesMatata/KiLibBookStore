from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('pay/', views.pay, name='pay'),
    path('callback/', views.LNMCallbackUrlAPIView.as_view(), name='callback'),
    path('confirmPay/<int:id>', views.confirmPay, name='confirmPay'),
]
