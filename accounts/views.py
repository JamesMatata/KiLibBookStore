from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.decorators.http import require_POST
from validate_email import validate_email

from accounts.forms import UserEditForm
from accounts.models import Seller
from accounts.token import account_activation_token
from orders.models import Order, OrderItem, BookLease, LeasedItem
from store.models import Product

from django.contrib.auth import get_user_model

User = get_user_model()


# from orders.models import Order, OrderItem


@login_required
def edit_details(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)

        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)

    return render(request,
                  'accounts/dashboard/edit_details.html', {'user_form': user_form})


@login_required
def delete_user(request):
    user = User.objects.get(username=request.user)
    user.is_active = False
    user.save()
    logout(request)
    return redirect('account:delete_confirmation')


@login_required
def wishlist(request):
    products = Product.objects.filter(users_wishlist=request.user)
    return render(request, 'accounts/dashboard/user_wish_list.html', {"wishlist": products})


@login_required
def wishlist(request):
    products = Product.objects.filter(users_wishlist=request.user)
    return render(request, 'accounts/dashboard/user_wish_list.html', {"wishlist": products})


@login_required
def orders(request):
    purchases = Order.objects.filter(user=request.user)
    purchased_items = OrderItem.objects.all()
    leases = BookLease.objects.filter(user=request.user)
    leased_items = LeasedItem.objects.all()
    return render(request, 'accounts/dashboard/orders.html', {"purchases": purchases, "purchasedItems": purchased_items,
                                                              "leases": leases, "leasedItems": leased_items})


@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    if product.users_wishlist.filter(id=request.user.id).exists():
        product.users_wishlist.remove(request.user)
        messages.success(request, "You removed " + product.title + " from wishlist")
    else:
        product.users_wishlist.add(request.user)
        messages.success(request, "Added " + product.title + " to your Wishlist")
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@login_required
def dashboard(request):
    return render(request, 'accounts/dashboard/buyer_dashboard.html', {})


@login_required
def seller_dashboard(request):
    business = get_object_or_404(Seller, user=request.user)
    return render(request, 'accounts/dashboard/seller_dashboard.html', {'business': business})


def register(request):
    if request.method == 'POST':
        context = {'has_error': False, 'data': request.POST}
        fname = request.POST.get('fname')
        lname = request.POST.get('sname')
        username = request.POST.get('uname')
        email = request.POST.get('email')
        usertype = request.POST.get('user')
        business_name = None
        business_email = None
        business_address = None
        if usertype == 'Seller':
            business_name = request.POST.get('business_name')
            business_email = request.POST.get('business_email')
            business_address = request.POST.get('business_address')
        password = request.POST.get('pass')
        password2 = request.POST.get('pass2')

        if len(password) < 8:
            messages.add_message(request, messages.ERROR,
                                 'Password should be at least 8 characters')
            context['has_error'] = True

        if password != password2:
            messages.add_message(request, messages.ERROR,
                                 'Password mismatch')
            context['has_error'] = True

        if not validate_email(email):
            messages.add_message(request, messages.ERROR,
                                 'Enter a valid email address')
            context['has_error'] = True

        if not username:
            messages.add_message(request, messages.ERROR,
                                 'Username is required')
            context['has_error'] = True

        if User.objects.filter(username=username).exists():
            messages.add_message(request, messages.ERROR,
                                 'Username is taken, choose another one')
            context['has_error'] = True

        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR,
                                 'Email is taken, choose another one')
            context['has_error'] = True

        if context['has_error']:
            return render(request, 'accounts/register.html', context)

        else:
            new_user = User.objects.create_user(username=username, email=email)
            new_user.set_password(password)
            new_user.first_name = fname
            new_user.last_name = lname
            if usertype == 'Seller':
                new_user.is_seller = True
            if usertype == 'Buyer':
                new_user.is_buyer = True
            new_user.is_active = False
            if usertype == 'Seller':
                new_business = Seller(user=new_user, business_name=business_name,
                                      business_email=business_email, business_address=business_address
                                      )
                new_business.save()
            new_user.save()
            # Setting-up email
            current_site = get_current_site(request)
            subject = 'Activate your Account'
            message = render_to_string('accounts/account_activation_email.html', {
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': account_activation_token.make_token(new_user),
            })
            new_user.email_user(subject=subject, message=message)
            messages.success(request, 'Account creation was successful, confirm you email using the link send to '
                                      'activate.')
            return redirect('store:index')

    return render(request, 'accounts/register.html')


def account_activate(request, uidb64, token):
    uid = force_str(urlsafe_base64_decode(uidb64))
    new_user = User.objects.get(pk=uid)
    if new_user is not None and account_activation_token.check_token(new_user, token):
        new_user.is_active = True
        new_user.save()
        login(request, new_user)
        return redirect('store:index')
    else:
        return render(request, 'accounts/activation_invalid.html')


def buyer_login(request):
    if request.method == 'POST':
        uname = request.POST.get('uname')
        password = request.POST.get('pass')

        user = authenticate(request, username=uname, password=password)
        if user is not None and user.is_seller is False:
            login(request, user)
            messages.success(request, 'You have been successfully logged in')
            return redirect('store:index')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('accounts:buyer_login-page')

    return render(request, 'accounts/login.html', {})


def seller_login(request):
    if request.method == 'POST':
        uname = request.POST.get('uname')
        password = request.POST.get('pass')

        user = authenticate(request, username=uname, password=password)
        if user is not None and user.is_seller is not False:
            login(request, user)
            messages.success(request, 'You have been successfully logged in')
            return redirect('store:index')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('accounts:seller_login-page')

    return render(request, 'accounts/login.html', {})


def logoutuser(request):
    logout(request)
    return redirect('store:index')


def business_sells(request):
    total_paid = 0
    sold_items = OrderItem.objects.filter(product__created_by=request.user, order__billing_status=True)
    for item in sold_items:
        total_paid = item.quantity * item.price

    return render(request, 'seller/account/sales.html', {'sold_items': sold_items, 'total_paid': total_paid})


def business_leases(request):
    total_paid = 0
    leased_items = LeasedItem.objects.filter(product__created_by=request.user, Book_Lease__billing_status=True)
    for item in leased_items:
        total_paid = item.quantity * item.lease_rate

    return render(request, 'seller/account/leases.html', {'leased_items': leased_items, 'total_paid': total_paid})


@require_POST
def toggle_wishlist(request):
    product_id = request.POST.get('productid')
    product = get_object_or_404(Product, id=product_id)

    if product.users_wishlist.filter(id=request.user.id).exists():
        product.users_wishlist.remove(request.user)
        in_wishlist = False
        message = f'{product.title} has been removed from your wishlist. <a href="{reverse("accounts:wishlist")}">View Wishlist</a>'
    else:
        product.users_wishlist.add(request.user)
        in_wishlist = True
        message = f'{product.title} has been added to your wishlist. <a href="{reverse("accounts:wishlist")}">View Wishlist</a>'

    return JsonResponse({'in_wishlist': in_wishlist, 'message': message})
