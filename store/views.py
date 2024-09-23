from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from accounts.models import Seller
from store.models import Product, Category
from django.contrib.auth import get_user_model

from django.utils.text import slugify

User = get_user_model()


def index(request):
    posted_products = None
    products = Product.objects.filter(is_active=True)
    if request.user.is_authenticated:
        seller_posted_products = Product.objects.filter(created_by=request.user, is_active=True)
        posted_products = seller_posted_products
    return render(request, 'home-page/index.html', {'products': products, 'posted_products': posted_products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, in_stock=True)
    category = product.category
    seller = get_object_or_404(Seller, user=product.created_by)
    related_products = Product.objects.filter(category=category, in_stock=True, is_active=True)
    return render(request, 'store/details.html',
                  {'product': product, 'related_products': related_products, 'seller': seller})


def slugifing(word):
    slug = slugify(word)
    return slug


def add_product(request):
    if request.method == 'POST':
        user = request.user
        book_name = request.POST.get('book_name')
        book_category = request.POST.get('bookCategory')
        book_img = request.FILES['productImage']
        author = request.POST.get('book_name')
        slug = slugifing(book_name)
        description = request.POST.get('description')
        book_price = request.POST.get('bookPrice')
        book_lease_rates = request.POST.get('bookLeaseRates')
        in_stock = request.POST.get('bookInStock', '') == 'on'
        is_active = request.POST.get('bookIsActive', '') == 'on'

        new_product = Product.objects.create(category=get_object_or_404(Category, name=book_category), title=book_name,
                                             created_by=user, slug=slug,
                                             author=author, description=description, image=book_img,
                                             price=book_price, in_stock=in_stock, is_active=is_active,
                                             book_lease_rates=book_lease_rates
                                             )
        new_product.save()
        return redirect('store:index')

    return render(request, 'seller/add_product.html', {})


def edit_product_details(request, id):
    product = Product.objects.get(id=id)
    if request.method == 'POST':
        product.title = request.POST.get('bookName')
        book_category = request.POST.get('bookCategory')
        product.category = get_object_or_404(Category, name=book_category)
        if 'productImage' in request.FILES:
            product.image = request.FILES['productImage']
        product.author = request.POST.get('author')
        product.description = request.POST.get('description')
        product.price = request.POST.get('bookPrice')
        product.book_lease_rates = request.POST.get('bookLeaseRates')
        in_stock = request.POST.get('bookInStock', '') == 'on'
        product.in_stock = in_stock
        is_active = request.POST.get('bookIsActive', '') == 'on'
        product.is_active = is_active

        product.save()

        return HttpResponseRedirect(reverse('store:index'))

    return render(request, 'seller/edit-product_details.html', {'product': product})


def category_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    if request.user.is_authenticated and request.user.is_buyer is not True:
        seller_posted_category_books = Product.objects.filter(category=category, created_by=request.user,
                                                              is_active=True)
        return render(request, 'store/category.html', {'seller_posted_category_books': seller_posted_category_books,
                                                       'category': category})
    else:
        products = Product.objects.filter(category=category, is_active=True)
        return render(request, 'store/category.html', {'products': products, 'category': category})


def searched_items(request):
    if request.method == "POST":
        searched = request.POST.get('searchBar', '').strip()
        if not searched:
            messages.error(request, "Search query cannot be empty.")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        if request.user.is_authenticated and request.user.is_buyer:
            items = Product.objects.filter(title__icontains=searched, is_active=True)
        elif request.user.is_authenticated and request.user.is_seller:
            items = Product.objects.filter(title__icontains=searched, is_active=True, created_by=request.user)
        else:
            items = Product.objects.filter(title__icontains=searched, is_active=True)

        if items.exists():
            return render(request, 'store/searched_items.html', {'searched': searched, 'items': items})
        else:
            messages.info(request, "No books found")
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))


def delete_product(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    return HttpResponseRedirect(reverse('store:index'))
