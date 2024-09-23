from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404

from orders.models import Order, BookLease
from payment.models import LNMOnline
from payment.views import lipa_na_mpesa
from wallet.models import Wallet


def wallet_index(request):
    wallet = get_object_or_404(Wallet, user=request.user)
    balance = wallet.balance
    usable_balance = wallet.usable_amount
    locked_balance = wallet.amount_locked

    return render(request, 'wallet/wallet.html', {
        'balance': balance,
        'usable_balance': usable_balance,
        'locked_balance': locked_balance
    })


def purchase_with_wallet(request, id):
    order = get_object_or_404(Order, id=id)
    wallet = get_object_or_404(Wallet, user=request.user)
    amount_to_pay = order.total_paid

    if amount_to_pay <= wallet.usable_amount:
        wallet.balance -= amount_to_pay
        wallet.usable_amount -= amount_to_pay
        wallet.save()
        order.billing_status = True
        order.save()
        messages.success(request, 'Purchase completed successfully.')
    else:
        return redirect('wallet:payment_failed')

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def lease_with_wallet(request, id):
    lease = get_object_or_404(BookLease, id=id)
    wallet = get_object_or_404(Wallet, user=request.user)
    amount_to_pay = lease.total_paid

    if amount_to_pay <= wallet.usable_amount:
        wallet.balance -= amount_to_pay
        wallet.usable_amount -= amount_to_pay
        wallet.save()
        lease.billing_status = True
        lease.save()
        messages.success(request, 'Lease completed successfully.')
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
        messages.success(request, 'Deposit initiated, please complete the transaction on your phone.')
        return redirect('wallet:confirm_deposit')

    return render(request, 'wallet/deposit.html')


def confirm_deposit(request):
    if request.method == 'POST':
        receipt_no = request.POST.get('receiptNo')
        transaction = get_object_or_404(LNMOnline, MpesaReceiptNumber=receipt_no, is_used=False)

        if transaction:
            wallet = get_object_or_404(Wallet, user=request.user)
            wallet.balance += transaction.Amount
            wallet.usable_amount += transaction.Amount
            wallet.save()
            transaction.is_used = True
            transaction.save()
            messages.success(request, 'Deposit confirmed successfully.')
            return redirect('wallet:wallet_index')
        else:
            messages.error(request, 'Invalid receipt number')
            return redirect('wallet:deposit')

    return render(request, 'wallet/confirm_deposit.html')