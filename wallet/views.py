import base64

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth

from KiLibBookStore.settings import MPESA_SHORTCODE, MPESA_PASSKEY, MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET
from payment.models import LNMOnline
from payment.serializer import LNMOnlineSerializer
from wallet.models import Wallet

unformatted_time = datetime.now()
formatted_time = unformatted_time.strftime("%Y%m%d%H%M%S")

data_to_encode = MPESA_SHORTCODE + MPESA_PASSKEY + formatted_time
encoded_string_p = base64.b64encode(data_to_encode.encode())
decoded_password = encoded_string_p.decode('utf-8')

consumer_key = MPESA_CONSUMER_KEY
consumer_secret = MPESA_CONSUMER_SECRET
access_token_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
r = requests.get(access_token_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
json_response = r.json()
my_access_token = json_response['access_token']


def wallet_index(request):
    wallet = get_object_or_404(Wallet, user=request.user)
    balance = wallet.balance

    return render(request, 'wallet/wallet.html', {'balance': balance})


def deposit_to_wallet(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        amount = request.POST.get('amount')

        access_token = my_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        pay_request = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": decoded_password,
            "Timestamp": formatted_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone,

            "CallBackURL": "https://b463-41-89-22-3.ngrok-free.app/pay/callback/",
            "AccountReference": "12345678",
            "TransactionDesc": "Buy books",
        }
        requests.post(api_url, json=pay_request, headers=headers)

        return redirect('store:index')
    return render(request, 'wallet/deposit.html', {})


def confirm_deposit(request):
    user = request.user
    wallet = get_object_or_404(Wallet, user=user)
    balance = wallet.balance
    if request.method == 'POST':
        receipt_no = request.POST.get('receiptNo')
        transaction = LNMOnline.objects.filter(MpesaReceiptNumber=receipt_no, is_used=True)
        if not transaction:
            wallet.balance = balance + transaction.Amount
            wallet.save()
            transaction.is_used = True
            transaction.save()
            return redirect('wallet:wallet_index')
        else:
            messages.error(request, 'Invalid receipt number')
            return redirect('wallet:deposit')
    return render(request, 'wallet/confirm_deposit.html', {})
