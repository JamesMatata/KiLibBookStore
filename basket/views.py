from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from store.models import Product, County, CountyDeliveryCharge
from .basket import Basket


class BasketSummaryView(View):
    def get(self, request, *args, **kwargs):
        basket = Basket(request)
        counties = County.objects.all()
        wishlist = []
        if request.user.is_authenticated:
            wishlist = Product.objects.filter(users_wishlist=request.user).values_list('id', flat=True)
        return render(request, 'basket/summary.html', {'basket': basket, 'wishlist': wishlist, 'counties': counties})


class BasketAddView(View):
    def post(self, request, *args, **kwargs):
        basket = Basket(request)
        if request.POST.get('action') == 'post':
            product_id = int(request.POST.get('productid'))
            product_qty = int(request.POST.get('productqty'))
            product = get_object_or_404(Product, id=product_id)
            basket.add(product=product, qty=product_qty)

            basketqty = basket.__len__()
            response = JsonResponse({'qty': basketqty})
            return response


class BasketDeleteView(View):
    def post(self, request, *args, **kwargs):
        basket = Basket(request)
        if request.POST.get('action') == 'post':
            product_id = int(request.POST.get('productid'))
            basket.delete(product=product_id)

            basketqty = basket.__len__()
            baskettotal = basket.get_total_price()
            response = JsonResponse({'qty': basketqty, 'subtotal': baskettotal})
            return response


class BasketUpdateView(View):
    def post(self, request, *args, **kwargs):
        basket = Basket(request)
        if request.POST.get('action') == 'post':
            product_id = int(request.POST.get('productid'))
            product_qty = int(request.POST.get('productqty'))
            basket.update(product=product_id, qty=product_qty)

            basketqty = basket.__len__()
            baskettotal = basket.get_total_price()
            response = JsonResponse({'qty': basketqty, 'subtotal': baskettotal})
            return response


class GetDeliveryCostView(View):
    def get(self, request, *args, **kwargs):
        delivery_method = request.GET.get('delivery_method')
        county_id = request.GET.get('county_id')
        county = get_object_or_404(County, id=county_id)
        delivery_charge = get_object_or_404(CountyDeliveryCharge, county=county)

        if delivery_method == 'door-delivery':
            delivery_cost = delivery_charge.door_delivery_charge
        elif delivery_method == 'pickup-point':
            delivery_cost = delivery_charge.pickup_point_charge
        else:
            delivery_cost = 0  # No charge for in-store pickup

        return JsonResponse({'delivery_cost': delivery_cost})
