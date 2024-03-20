import base64
from datetime import datetime
from itertools import product

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django_daraja.mpesa.core import MpesaClient
from requests.auth import HTTPBasicAuth
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User

from KiLibBookStore.settings import MPESA_SHORTCODE, MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_PASSKEY
from orders.models import Order, OrderItem
from payment.models import LNMOnline
from payment.serializer import LNMOnlineSerializer
from store.models import Product

from basket.basket import Basket

from django.urls import reverse

# callback_url = request.build_absolute_url(reverse('callback'))
# callback_url = reverse('callback')
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


@login_required
def pay(request):
    basket = Basket(request)
    total = str(basket.get_total_price())
    total = int(total)
    if request.method == 'POST':
        user_id = request.user.id
        full_name = request.POST.get('full_name')
        deliveryPoint = request.POST.get('dp1')
        deliveryPoint2 = request.POST.get('dp2')
        phone = request.POST.get('phone_number')
        email = request.POST.get('email')
        county = request.POST.get('county')

        access_token = my_access_token
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % access_token}
        pay_request = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": decoded_password,
            "Timestamp": formatted_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": total,
            "PartyA": phone,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone,

            "CallBackURL": "https://b463-41-89-22-3.ngrok-free.app/pay/callback/",
            "AccountReference": "12345678",
            "TransactionDesc": "Buy books",
        }
        requests.post(api_url, json=pay_request, headers=headers)

        order = Order.objects.create(user_id=user_id, full_name=full_name,
                                     county=county, deliveryPoint=deliveryPoint, deliveryPoint2=deliveryPoint2,
                                     phone=phone, total_paid=total, email=email
                                     )
        order_id = order.pk
        for item in basket:
            OrderItem.objects.create(order_id=order_id, product=item['product'], price=item['price'], quantity=item['qty'])
        order.save()

        messages.success(request, 'Your order has been placed successfully, confirm the transaction to complete.')
        return redirect('store:index')
    return render(request, 'payment/pay.html', {})


class LNMCallbackUrlAPIView(CreateAPIView):
    queryset = LNMOnline.objects.all()
    serializer_class = LNMOnlineSerializer

    def create(self, request, *args, **kwargs):
        merchant_request_id = request.data['Body']['stkCallback']['MerchantRequestID']
        checkout_request_id = request.data['Body']['stkCallback']['CheckoutRequestID']
        result_code = request.data['Body']['stkCallback']['ResultCode']
        result_description = request.data['Body']['stkCallback']['ResultDesc']
        amount = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
        mpesa_receipt_number = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
        transaction_date = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value']
        phone_number = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']

        from datetime import datetime
        str_transaction_date = str(transaction_date)
        transaction_datetime = datetime.strptime(str_transaction_date, "%Y%m%d%H%M%S")

        model = LNMOnline.objects.create(CheckoutRequestID=checkout_request_id, MerchantRequestID=merchant_request_id,
                                         ResultCode=result_code, ResultDesc=result_description, Amount=amount,
                                         MpesaReceiptNumber=mpesa_receipt_number, TransactionDate=transaction_datetime,
                                         PhoneNumber=phone_number
                                         )
        model.save()


def confirmPay(request, id):
    order = get_object_or_404(Order, id=id)
    if request.method == 'GET':
        receipt_no = request.GET.get('receiptnumber')
        transaction = get_object_or_404(LNMOnline, MpesaReceiptNumber=receipt_no, is_used=False)
        if transaction is not None and transaction.Amount == order.total_paid:
            order.receipt_No = receipt_no
            order.billing_status = True
            order.save()
            transaction.is_used = True
            transaction.save()
        else:
            messages.error(request, 'Invalid receipt number')
            return redirect('accounts:order')
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
