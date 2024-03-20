from django.urls import path

from wallet.views import deposit_to_wallet, wallet_index, confirm_deposit

app_name = 'wallet'

urlpatterns = [
    path('wallet', wallet_index, name="wallet_index"),
    path('deposit', deposit_to_wallet, name="deposit"),
    path('confirm-deposit', confirm_deposit, name="confirm_deposit"),
]
