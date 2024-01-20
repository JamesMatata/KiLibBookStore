from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from store.models import Product, Category


def all_products(request):
    products = Product.objects.all()
    return render(request, 'Home-page/buyer_index.html', {'products': products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, in_stock=True)
    category = product.category
    related_products = Product.objects.filter(category=category, in_stock=True)
    return render(request, 'store/details.html', {'product': product, 'related_products':related_products})


def category_list(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    product = Product.objects.filter(category=category)
    return render(request, 'store/category.html', {'category': category, 'product': product})


def searched_items(request):
    if request.method == "POST":
        searched = request.POST['searchBar']
        items = Product.objects.filter(title__contains=searched)
        if items.exists():
            return render(request, 'store/searched_items.html', {'searched': searched, 'items': items})
        else:
            messages.success(request, "No books found")
        return HttpResponseRedirect(request.META["HTTP_REFERER"])
    return render(request, 'Home-page/buyer_index.html')
