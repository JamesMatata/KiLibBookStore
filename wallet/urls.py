from django.urls import path

from wallet.views import deposit_to_wallet, wallet_index, confirm_deposit, purchase_with_wallet, payment_failed, \
    lease_with_wallet

app_name = 'wallet'

urlpatterns = [
    path('wallet', wallet_index, name="wallet_index"),
    path('deposit', deposit_to_wallet, name="deposit"),
    path('confirm-deposit', confirm_deposit, name="confirm_deposit"),
    path('purchase/<int:id>', purchase_with_wallet, name="purchase_with_wallet"),
    path('lease/<int:id>', lease_with_wallet, name="lease_with_wallet"),
    path('payment_failed', payment_failed, name="payment_failed"),
]
