import base64

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime

from KiLibBookStore.settings import MPESA_SHORTCODE, MPESA_PASSKEY, MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET
from orders.models import Order, Book_Lease
from payment.models import LNMOnline
from payment.views import lipa_na_mpesa
from wallet.models import Wallet


def wallet_index(request):
    wallet = get_object_or_404(Wallet, user=request.user)
    balance = wallet.balance
    usable_balance = wallet.usable_amount
    locked_balance = wallet.amount_locked

    return render(request, 'wallet/wallet.html',
                  {'balance': balance, 'usable_balance': usable_balance, 'locked_balance': locked_balance})


def purchase_with_wallet(request, id):
    wallet = get_object_or_404(Wallet, user=request.user)
    wallet_usable_balance = wallet.usable_amount
    order = get_object_or_404(Order, id=id)
    amount_to_pay = order.total_paid
    if amount_to_pay < wallet_usable_balance:
        wallet.balance -= amount_to_pay
        wallet.usable_amount = wallet.balance - wallet.amount_locked
        wallet.save()
        order.billing_status = True
        order.save()
    else:
        return redirect('wallet:payment_failed')
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def lease_with_wallet(request, id):
    wallet = get_object_or_404(Wallet, user=request.user)
    wallet_usable_balance = wallet.usable_amount
    lease = get_object_or_404(Book_Lease, id=id)
    amount_to_pay = lease.total_paid
    if amount_to_pay < wallet_usable_balance:
        wallet.balance -= amount_to_pay
        wallet.usable_amount = wallet.balance - wallet.amount_locked
        wallet.save()
        lease.billing_status = True
        lease.save()
    else:
        return redirect('wallet:payment_failed')
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def payment_failed(request):
    return render(request, 'wallet/payment_with_wallet_failed.html')


def deposit_to_wallet(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        amount = request.POST.get('amount')

        lipa_na_mpesa(amount, phone)

        return redirect('wallet:confirm_deposit')
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
            wallet.usable_amount = wallet.balance - wallet.amount_locked
            wallet.save()
            transaction.is_used = True
            transaction.save()
            return redirect('wallet:wallet_index')
        else:
            messages.error(request, 'Invalid receipt number')
            return redirect('wallet:deposit')
    return render(request, 'wallet/confirm_deposit.html', {})
