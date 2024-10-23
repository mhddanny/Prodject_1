from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404

from profiles.models import Province, Address
from store.models import Product, ProductItem, Variation, ProductPaket
from . models import Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.db.models import Q

import http.client
import json

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

def add_cart(request, product_id):
    current_user = request.user
    # print('request :', request.POST)
    color = request.POST['color']
    size = request.POST['size']
    product = ProductItem.objects.filter(product=product_id, variation__variation_value__iexact=color).filter(variation__variation_value__iexact=size).get()

    #if the user authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product_item__exact=product.id, varian_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                    
                except:
                    pass

        is_cart_item_exits = CartItem.objects.filter(product__exact=product.id, user=current_user).exists() 
        if is_cart_item_exits :
            cart_item = CartItem.objects.get(product__exact=product.id, user=current_user)
            
            if cart_item:
                # inrease the cart item quantity
                item = CartItem.objects.get(product__exact=product.id, id__exact=cart_item.id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)

                item.save()
        else :
            cart_item = CartItem.objects.create(
                product= product,
                quantity = 1,
                user = current_user,

            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            
            cart_item.save()
        return redirect('cart')
    #it then user is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item.lower()
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product_item__exact=product.id, varian_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) #get the cart using the cart_id persent in the session 
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
        cart.save()

        is_cart_item_exits = CartItem.objects.filter(product__exact=product.id, cart=cart).exists()
        if is_cart_item_exits :
            cart_item = CartItem.objects.filter(product__exact=product.id, cart=cart)
            # exixting_variations ->database
            # corret variation -> product_variation
            # item_id -> database
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variantion = item.variation.all()
                ex_var_list.append(list(existing_variantion))
                id.append(item.id)
            
            print(ex_var_list)

            if product_variation in ex_var_list:
                # inrease the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product__exact=product.id, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_variation) > 0:
                    item.variation.clear()
                    item.variation.add(*product_variation)

                item.save()
        else :
            cart_item = CartItem.objects.create(
                product= product,
                quantity = 1,
                cart = cart,

            )
            if len(product_variation) > 0:
                cart_item.variation.clear()
                cart_item.variation.add(*product_variation)
            
            cart_item.save()
        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    
    product = get_object_or_404(ProductItem, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
        
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    
    product= get_object_or_404(ProductItem, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        grand_total = total 
    
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'grand_total' : grand_total,
    }
    return render(request, 'store/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        total_weight = 0
        province = Province.objects.all()
        address_all = Address.objects.filter(user=request.user).order_by('-updated_at')
        address = address_all.filter(default=True).first()
        

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        # Quantity
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

            product_paket = ProductPaket.objects.get(product=cart_item.product.product.id)
            sub_weight = product_paket.weight * cart_item.quantity
            # print('sub_weight :', sub_weight)
            total_weight += sub_weight #Total Weight
                    
        tax=(2 * total)/100
        grand_total = total + tax
        
    except ObjectDoesNotExist:
        pass

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax' : tax, 
        'grand_total' : grand_total,
        'total_weight': total_weight,
        'prov': province,
        'address_all': address_all,
        'address': address,  # User Address Data
    }

    return render(request, 'store/checkout.html', context)

@login_required(login_url='login')
def getCourier(request):
    data = {}
    if request.method == 'POST':
        # print('data', request.POST)
        destination = request.POST['destination']
        weight = request.POST['weight']
        courier = request.POST['courier']

        api_Key = settings.RAJA_ONGKIR_KEY
        conn = http.client.HTTPSConnection("api.rajaongkir.com")

        payload =  "origin=152&destination="+str(destination)+"&weight="+str(weight)+"&courier="+str(courier)

        headers = {
            'key': api_Key,
            'content-type': "application/x-www-form-urlencoded",
            
        }

        conn.request("POST", "/starter/cost", payload, headers)

        res = conn.getresponse()
        data = res.read()
        conn.close()
        # print('data', data.decode("utf-8") )
        costs = json.loads(data)
        # Loop Data Json
        # print(costs)
        for cost in costs['rajaongkir']['results']:
            # cost = cost['description']+' '+cost['cost'][0]['etd']+' days'
            delivery = cost
            # print('cost', delivery)  
            data = {
                'data': delivery
            }

        response = JsonResponse(data, safe=False)
        return response
    else:
        response = JsonResponse({'status':'false','message':messages}, status=500)
        return response
    
@login_required(login_url='login')
def addDelivery(request):
    if not request.user.is_authenticated:
        return redirect('login')
        
    try:
        if request.method == 'POST':
            address = Address()
            address.first_name = request.POST['first_name']
            address.last_name = request.POST['last_name']
            address.email = request.POST['email']
            address.phone = request.POST['phone']
            address.address_line_1 = request.POST['address_line_1']
            address.address_line_2 = request.POST['address_line_2']
            address.district_id = request.POST['district_id']
            address.default = True
            address.user_id = request.user.id
            address.save()

            # Update default address
            if address.default:
                Address.objects.filter(user=request.user).exclude(id=address.id).update(default=False)
                address.save()
            else:
                Address.objects.filter(user=request.user).update(default=True).update(default=False)
                address.save()

            messages.success(request, 'Your address has been created')
            return redirect('checkout')
        else:
            messages.error(request, 'Please enter your address first and try again ')
            
    except Exception as e:
        print('Error:', e)
        messages.error(request, 'An error occurred while trying to add your address')
        return redirect('checkout')