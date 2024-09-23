import base64
from datetime import datetime

import requests
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from KiLibBookStore.settings import MPESA_SHORTCODE, MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET, MPESA_PASSKEY
from orders.models import Order, OrderItem, BookLease, LeasedItem
from payment.models import LNMOnline
from payment.serializer import LNMOnlineSerializer

from basket.basket import Basket
from store.models import County

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
    token_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    credentials = f"{consumer_key_p}:{consumer_secret_p}"
    base64_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {'Authorization': f'Basic {base64_credentials}'}

    try:
        response = requests.get(token_url, headers=headers)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")

        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
        access_token = data.get('access_token')
        if not access_token:
            raise ValueError("Failed to obtain access token.")
        return access_token
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def lipa_na_mpesa(amount, phone_number):
    try:
        access_token = generate_access_token(consumer_key, consumer_secret)
        if not access_token:
            raise ValueError("Invalid access token.")

        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        amount = int(amount)

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

        response = requests.post(api_url, json=pay_request, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        print("Response JSON:", response_data)
        return response_data
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except ValueError as e:
        print(f"Error: {e}")
        return None


def process_payment(request):
    if not request.user.is_authenticated:
        return redirect('accounts:buyer_login_page')

    wallet = get_object_or_404(Wallet, user=request.user)
    wallet_balance = wallet.balance
    usable_balance = wallet.usable_amount
    basket = Basket(request)
    counties = County.objects.all()

    ownership_option = request.GET.get('ownership_options')
    selected_county_id = request.GET.get('county', '')
    delivery_method = request.GET.get('delivery_method')
    selected_lease_weeks = int(request.GET.get('lease_weeks', 0))
    purchase_subtotal = float(request.GET.get('purchase_subtotal', 0))
    lease_subtotal = float(request.GET.get('lease_subtotal', 0))
    passed_total = float(request.GET.get('total-costs-input', 0))

    if request.method == 'POST':
        user_id = request.user.id
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        ownership_option_selected = request.POST.get('ownership_option')
        delivery_method_selected = request.POST.get('delivery_method')
        payment_method = request.POST.get('payment_method')
        mpesa_phone = request.POST.get('phone_number') if payment_method == 'm-pesa' else ''

        county = request.POST.get('county', '')
        delivery_point = request.POST.get('dp1', '')
        delivery_point2 = request.POST.get('dp2', '')
        pick_up_point = request.POST.get('pick-up-point', '')

        delivery_costs = int(float(request.POST.get('delivery_costs', 0)))
        total_costs = int(float(request.POST.get('total_costs_input', 0)))
        purchase_sub_total = int(float(request.POST.get('purchase_sub_total', 0)))

        if ownership_option_selected == 'lease':
            lease_weeks = int(request.POST.get('lease_weeks', 1))

            if purchase_sub_total > usable_balance:
                return render(request, 'payment/less_wallet_balance.html', {'lease_costs': total_costs})

            else:
                new_lease = BookLease.objects.create(
                    user_id=user_id, full_name=full_name, delivery_method=delivery_method_selected,
                    delivery_costs=delivery_costs, ownership_option=ownership_option_selected,
                    total_paid=total_costs, email=email,
                    leased_weeks=lease_weeks, billing_status=False,
                    payment_method=payment_method, purchase_cost=purchase_sub_total
                )
                if payment_method == 'm-pesa':
                    new_lease.mpesa_phone = mpesa_phone

                if delivery_method_selected == 'door-delivery':
                    new_lease.county = county
                    new_lease.delivery_point = delivery_point
                    new_lease.delivery_point2 = delivery_point2
                elif delivery_method_selected == 'pickup-point':
                    new_lease.county = county
                    new_lease.pick_up_point = pick_up_point

                new_lease.save()

                for item in basket:
                    LeasedItem.objects.create(
                        Book_Lease_id=new_lease.pk, product=item['product'], lease_rate=item['book_lease_rates'],
                        quantity=item['qty']
                    )

                if payment_method == 'm-pesa':
                    wallet.amount_locked += purchase_sub_total
                    lipa_na_mpesa(total_costs, mpesa_phone)
                    messages.success(request,
                                     'Your lease order has been placed successfully, confirm the transaction to complete.')
                    return redirect('accounts:order')
                else:
                    wallet.amount_locked += purchase_sub_total
                    if total_costs <= usable_balance:
                        wallet.balance -= total_costs
                        wallet.save()
                        new_lease.billing_status = True
                        new_lease.save()
                        messages.success(request, 'Your lease order has been completed. Wait for delivery.')
                    else:
                        return redirect('wallet:payment_failed')

        elif ownership_option_selected == 'purchase':
            new_order = Order.objects.create(
                user_id=user_id, full_name=full_name, delivery_method=delivery_method_selected,
                delivery_costs=delivery_costs, mpesa_phone=mpesa_phone,
                total_paid=total_costs, email=email, billing_status=False
            )

            if delivery_method_selected == 'door-delivery':
                new_order.county = county
                new_order.delivery_point = delivery_point
                new_order.delivery_point2 = delivery_point2
            elif delivery_method_selected == 'pickup-point':
                new_order.county = county
                new_order.pick_up_point = pick_up_point

            new_order.save()

            for item in basket:
                OrderItem.objects.create(
                    order_id=new_order.pk, product=item['product'], price=item['price'], quantity=item['qty']
                )

            if payment_method == 'm-pesa':
                lipa_na_mpesa(total_costs, mpesa_phone)
                messages.success(request,
                                 'Your order has been placed successfully, confirm the transaction to complete.')
                return redirect('accounts:order')
            else:
                wallet.balance -= total_costs
                wallet.usable_amount = wallet.balance - wallet.amount_locked
                wallet.save()
                new_order.billing_status = True
                new_order.save()
                messages.success(request, 'Your order has been completed. Wait for delivery.')

    return render(request, 'payment/purchase.html', {
        'usable_balance': usable_balance,
        'wallet_balance': wallet_balance,
        'lease_weeks': selected_lease_weeks,
        'ownership_option': ownership_option,
        'selected_county_id': selected_county_id,
        'counties': counties,
        'delivery_method': delivery_method,
        'purchase_subtotal': purchase_subtotal,
        'lease_subtotal': lease_subtotal,
        'passed_total': passed_total,
    })


class LNMCallbackUrlAPIView(CreateAPIView):
    queryset = LNMOnline.objects.all()
    serializer_class = LNMOnlineSerializer

    def create(self, request, *args, **kwargs):
        try:
            merchant_request_id = request.data['Body']['stkCallback']['MerchantRequestID']
            checkout_request_id = request.data['Body']['stkCallback']['CheckoutRequestID']
            result_code = request.data['Body']['stkCallback']['ResultCode']
            result_description = request.data['Body']['stkCallback']['ResultDesc']
            amount = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][0]['Value']
            mpesa_receipt_number = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][1]['Value']
            transaction_date = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][3]['Value']
            phone_number = request.data['Body']['stkCallback']['CallbackMetadata']['Item'][4]['Value']

            str_transaction_date = str(transaction_date)
            transaction_datetime = datetime.strptime(str_transaction_date, "%Y%m%d%H%M%S")

            model = LNMOnline.objects.create(
                CheckoutRequestID=checkout_request_id, MerchantRequestID=merchant_request_id,
                ResultCode=result_code, ResultDesc=result_description, Amount=amount,
                MpesaReceiptNumber=mpesa_receipt_number, TransactionDate=transaction_datetime,
                PhoneNumber=phone_number
            )
            model.save()
            return Response({"status": "Success"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Callback handling failed: {e}")
            return Response({"status": "Failed"}, status=status.HTTP_400_BAD_REQUEST)


def confirmPurchase(request, purchase_id):
    order = get_object_or_404(Order, id=purchase_id)
    if request.method == 'GET':
        receipt_no = request.GET.get('receiptnumber')
        transaction = get_object_or_404(LNMOnline, MpesaReceiptNumber=receipt_no, is_used=False)
        if transaction and transaction.Amount == order.total_paid:
            order.receipt_No = receipt_no
            order.billing_status = True
            order.save()
            transaction.is_used = True
            transaction.save()
        else:
            messages.error(request, 'Invalid receipt number')
            return redirect('accounts:order')
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def confirmLease(request, lease_id):
    lease = get_object_or_404(BookLease, id=lease_id)
    if request.method == 'GET':
        receipt_no = request.GET.get('receiptnumber')
        transaction = get_object_or_404(LNMOnline, MpesaReceiptNumber=receipt_no, is_used=False)
        if transaction and transaction.Amount == lease.total_paid:
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

