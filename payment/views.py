import base64
from datetime import datetime

import requests
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.generics import CreateAPIView

from KiLibBookStore.settings import MPESA_SHORTCODE, MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_PASSKEY
from orders.models import Order, OrderItem, Book_Lease, LeasedItem
from payment.models import LNMOnline
from payment.serializer import LNMOnlineSerializer

from basket.basket import Basket

from wallet.models import Wallet

unformatted_time = datetime.now()
formatted_time = unformatted_time.strftime("%Y%m%d%H%M%S")

data_to_encode = MPESA_SHORTCODE + MPESA_PASSKEY + formatted_time
encoded_string_p = base64.b64encode(data_to_encode.encode())
decoded_password = encoded_string_p.decode('utf-8')

consumer_key = MPESA_CONSUMER_KEY
consumer_secret = MPESA_CONSUMER_SECRET


# noinspection PyCompatibility
def generate_access_token(consumer_key_p, consumer_secret_p):
    # Endpoint for obtaining OAuth access token
    token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    # Base64 encode the consumer key and consumer secret
    credentials = f"{consumer_key_p}:{consumer_secret_p}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()

    # Set headers with Authorization
    headers = {
        'Authorization': f'Basic {base64_credentials}'
    }

    # Make a POST request to obtain the access token
    response = requests.post(token_url, headers=headers)

    # Parse the response JSON
    data = response.json()

    # Extract the access token from the response
    access_token = data.get('access_token')

    return access_token


def lipa_na_mpesa(amount, phone_number):
    access_token = generate_access_token(consumer_key, consumer_secret)
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer %s" % access_token}
    pay_request = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": decoded_password,
        "Timestamp": formatted_time,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone_number,

        "CallBackURL": "https://giving-finer-foal.ngrok-free.app/pay/callback/",
        "AccountReference": "12345678",
        "TransactionDesc": "Buy books",
    }
    requests.post(api_url, json=pay_request, headers=headers)


def pay(request):
    if not request.user.is_authenticated:
        return redirect('accounts:buyer_login-page')
    else:
        wallet = get_object_or_404(Wallet, user=request.user)
        wallet_balance = wallet.balance
        usable_balance = wallet.usable_amount
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
            payment_method = request.POST.get('payment_method')

            new_order = Order.objects.create(user_id=user_id, full_name=full_name,
                                             county=county, deliveryPoint=deliveryPoint, deliveryPoint2=deliveryPoint2,
                                             phone=phone, total_paid=total, email=email, billing_status=False
                                             )
            order_id = new_order.pk
            for item in basket:
                OrderItem.objects.create(order_id=order_id, product=item['product'], price=item['price'],
                                         quantity=item['qty'])
            new_order.save()

            if payment_method == 'M-Pesa':
                lipa_na_mpesa(total, phone)

                messages.success(request,
                                 'Your order has been placed successfully, confirm the transaction to complete.')
                return redirect('accounts:order')

            else:
                wallet.balance -= total
                wallet.usable_amount = wallet.balance - wallet.amount_locked
                wallet.save()

                new_order.billing_status = True
                new_order.save()

                messages.success(request,
                                 'Your order has been completed. Wait for delivery')
                return redirect('accounts:order')

    return render(request, 'payment/purchase.html', {'total': total, 'usable_balance': usable_balance})


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


def confirmPurchase(request, id):
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


def confirmLease(request, id):
    lease = get_object_or_404(Book_Lease, id=id)
    if request.method == 'GET':
        receipt_no = request.GET.get('receiptnumber')
        transaction = get_object_or_404(LNMOnline, MpesaReceiptNumber=receipt_no, is_used=False)
        if transaction is not None and transaction.Amount == lease.total_paid:
            lease.receipt_No = receipt_no
            lease.billing_status = True
            lease.save()
            transaction.is_used = True
            transaction.save()
            wallet = get_object_or_404(Wallet, user=request.user)
            wallet.amount_locked += lease.purchase_cost
            wallet.save()
        else:
            messages.error(request, 'Invalid receipt number')
            return redirect('accounts:order')
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def leaseBook(request):
    if not request.user.is_authenticated:
        return redirect('accounts:buyer_login-page')
    else:
        wallet = get_object_or_404(Wallet, user=request.user)
        wallet_usable_balance = wallet.usable_amount
        basket = Basket(request)
        purchase_costs = str(basket.get_total_price())
        purchase_costs = int(purchase_costs)
        lease_costs = str(basket.get_total_lease_price())
        lease_costs = int(lease_costs)

        if purchase_costs > wallet_usable_balance:
            return render(request, 'payment/less_wallet_balance.html',
                          {'purchase_costs': purchase_costs})
        else:
            if request.method == 'POST':
                user_id = request.user.id
                full_name = request.POST.get('full_name')
                deliveryPoint = request.POST.get('dp1')
                deliveryPoint2 = request.POST.get('dp2')
                phone = request.POST.get('phone_number')
                email = request.POST.get('email')
                county = request.POST.get('county')
                lease_weeks = request.POST.get('weekNo')
                payment_method = request.POST.get('payment_method')
                lease_total_costs = lease_costs * int(lease_weeks)

                new_lease = Book_Lease.objects.create(user_id=user_id, full_name=full_name,
                                                      county=county, deliveryPoint=deliveryPoint,
                                                      deliveryPoint2=deliveryPoint2,
                                                      phone=phone, total_paid=lease_total_costs, email=email
                                                      , purchase_cost=purchase_costs, leased_weeks=lease_weeks,
                                                      )
                lease_id = new_lease.pk
                for item in basket:
                    LeasedItem.objects.create(Book_Lease_id=lease_id, product=item['product'],
                                              lease_rate=item['book_lease_rates'],
                                              quantity=item['qty'])
                new_lease.save()

                if payment_method == 'M-Pesa':
                    lipa_na_mpesa(lease_total_costs, phone)

                    messages.success(request,
                                     'Your lease order has been placed successfully, confirm the transaction to '
                                     'complete.')
                    return redirect('accounts:order')

                else:
                    wallet = get_object_or_404(Wallet, user=request.user)
                    wallet_usable_balance = wallet.usable_amount
                    if lease_costs < wallet_usable_balance:
                        wallet.balance -= lease_costs
                        wallet.usable_amount = wallet.balance - wallet.amount_locked
                        wallet.save()
                        new_lease.billing_status = True
                        new_lease.save()
                    else:
                        return redirect('wallet:payment_failed')

            return render(request, 'payment/lease.html',
                          {'wallet_usable_balance': wallet_usable_balance, 'lease_costs': lease_costs})
