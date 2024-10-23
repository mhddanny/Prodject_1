from carts.models import Cart, CartItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from profiles.models import Address
from store.models import Product, ProductItem, ReviewRating

from store.forms import ReviewForm

from . models import Order, OrderProduct, Payment, OrderDelivery

import datetime
import json
import uuid
import midtransclient
import hashlib
import base64

MIDTRANS_CORE = midtransclient.CoreApi(
    is_production=not settings.DEBUG,
    server_key=settings.MIDTRANS['SERVER_KEY'],
    client_key=settings.MIDTRANS['CLIENT_KEY'],
)

MIDTRANS_SNAP = midtransclient.Snap(
    is_production=not settings.DEBUG,
    server_key=settings.MIDTRANS['SERVER_KEY'],
    client_key=settings.MIDTRANS['CLIENT_KEY'],
)

#Autorizations for transaction management midtranslation
def authorizationMenegment():
    client_key = settings.MIDTRANS['CLIENT_KEY']
    server_key = settings.MIDTRANS['SERVER_KEY'] 
    server_key = "Basic "+server_key+":"
    server_key_byte = server_key.encode("ascii")
    base64_string = base64.b64encode(server_key_byte)
    server = base64_string.decode("ascii")

    return server

@login_required(login_url='login')
def payment_proses(request):
    body = json.loads(request.body) 
    order_id = body['order_id']
    # print('order_id', order_id)

    order = Order.objects.get(user=request.user, is_ordered=False, order_number=order_id)
    # Cek Order object
    if not order:
        return JsonResponse(data = {'error': 'Invalid Order ID'}, status=400)

    transaction_status = MIDTRANS_CORE.transactions.status(str(order_id))
    print('payment_type', transaction_status)
    if not transaction_status:
        return JsonResponse(data = {'error': 'Invalid Transactions'}, status=400)

    # [5.A] Handle transaction status on your backend
    # Sample transaction_status handling logic
    if transaction_status['payment_type'] == 'credit_card':
        payment = Payment(
            user = request.user,
            payment_id = transaction_status['transaction_id'],
            payment_method = transaction_status['bank'],
            amount_paid = transaction_status['gross_amount'],
            payment_type = transaction_status['payment_type'],
            status = transaction_status['transaction_status'],
        )
        payment.save()
    elif transaction_status['payment_type'] == 'echannel':
        payment = Payment(
            user = request.user,
            payment_id = transaction_status['transaction_id'],
            payment_method = 'Mandiri Bill',
            amount_paid = transaction_status['gross_amount'],
            payment_type = transaction_status['payment_type'],
            status = transaction_status['transaction_status'],
        )
        payment.save()
    elif transaction_status['payment_type'] == 'bank_transfer':
            payment = Payment(
                user = request.user,
                payment_id = transaction_status['transaction_id'],
                payment_method = transaction_status['va_numbers'][0]['bank']+'_VA',
                amount_paid = transaction_status['gross_amount'],
                payment_type = transaction_status['payment_type'],
                status = transaction_status['transaction_status'],
            )
            payment.save()      
    elif transaction_status['payment_type'] == 'gopay':
        payment = Payment(
            user = request.user,
            payment_id = transaction_status['transaction_id'],
            payment_method = 'Gopay',
            amount_paid = transaction_status['gross_amount'],
            payment_type = transaction_status['payment_type'],
            status = transaction_status['transaction_status'],
        )
        payment.save()
    elif transaction_status['payment_type'] == 'qris':
        payment = Payment(
            user = request.user,
            payment_id = transaction_status['transaction_id'],
            payment_method = 'Shopeepay',
            amount_paid = transaction_status['gross_amount'],
            payment_type = transaction_status['payment_type'],
            status = transaction_status['transaction_status'],
        )
        payment.save()
    elif transaction_status['payment_type'] == 'cstore':
        payment = Payment(
            user = request.user,
            payment_id = transaction_status['transaction_id'],
            payment_method = 'C-Store',
            amount_paid = transaction_status['gross_amount'],
            payment_type = transaction_status['payment_type'],
            status = transaction_status['transaction_status'],
        )
        payment.save()

    # if transaction_status['transaction_status'] == 'capture':
    #     if fraud_status == 'challenge':
    #         # TODO set transaction status on your databaase to 'challenge'
    #         None
    #     elif fraud_status == 'accept':
    #         # TODO set transaction status on your databaase to 'success'
    #         None
    # elif transaction_status['transaction_status'] == 'settlement':
    #     payment.save()

    # Update order is_ordered
    if transaction_status['transaction_status'] == 'settlement' or transaction_status['transaction_status'] == 'capture' :
        order.payment = payment
        order.status = 'CONFIRM'
        order.is_ordered = True
        order.save()
    elif transaction_status['transaction_status'] == 'pending' :
        order.payment = payment
        order.status = 'PENDING'
        order.is_ordered = True
        order.save()
    elif transaction_status['transaction_status'] == 'deny' or transaction_status['transaction_status'] == 'failure':
        order.payment = payment
        order.status = 'CANCELLED'
        order.is_ordered = True
        order.save()

    cart_items = CartItem.objects.filter(user=request.user)

    #Cek Order status
    if order.is_ordered != True:
        return JsonResponse(data = {'error': 'Order not confirmed status'}, status=400)


    for item in cart_items:
        p = ProductItem.objects.get(id__exact=item.product.id)
        prod = float(p.price)
        IDProduct = p.id # product_item ID
        product_price = prod # product_item price 

        # inser to order by product in tabel orderproduct
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = IDProduct
        orderproduct.quantity = item.quantity
        orderproduct.product_price = product_price
        orderproduct.ordered = True
        orderproduct.save()

        # insert to order by product variation in tabel orderproductvariation many to many
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()
            
        # reduce the quantiry of the sold product
        product = ProductItem.objects.get(id=IDProduct)
        product.stock -= item.quantity
        product.save()

        # clarn cart
    CartItem.objects.filter(user=request.user).delete()

    # send ordered receiverd email to customer
    mail_subject = 'Thanks you for your order !'
    message = render_to_string('orders/order_vertification_email.html', {
            'user' : request.user,
            'order': order,
        })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send() 

    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id
    }
        
    return JsonResponse(data)

@login_required(login_url='login')
def payment_midtrants(request):
    product_price = 0
    total_cost = 0
    sub_total = 0
    total =  0
    quantity = 0
    body = json.loads(request.body)
    amount = body['amount']
        
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    # loop Address to get order

    # Cek Order object
    if not order:
        return JsonResponse(data = {'error': 'Invalid Order ID'}, status=400)

    # Get cart items
    cart_items = CartItem.objects.filter(user=request.user)
    
    # cek cart items
    if not cart_items:
        return JsonResponse(data = {'error': 'Cart is empty'}, status=400)

    # Loop cart items
    for cart_item in cart_items:
        cart_id = cart_item.id
        product = cart_item.product.product.name
        qty = cart_item.quantity

        quantity += cart_item.quantity
        item = ProductItem.objects.get(id__exact=cart_item.product.id)
        # Cek Order Product
        if not item:
            return JsonResponse(data = {'error': 'Invalid Product ID'}, status=400)
        
        product_price = item.price
        sub_total += (product_price * cart_item.quantity)#harga price
        print('subtotal : ', sub_total)

    tax = (2 * sub_total)/100 # Total the tax amount
    grand_total = sub_total + tax # Get the grand
    total_cost = order.orderdelivery.cost #Get total ongkos
    total += total_cost + grand_total # Total Buyers
    tota_all = int(total)
    print('Total :', total)

    # Build API parameter
    param = {
        "transaction_details": {
            "order_id": str(order.order_number),
            "gross_amount": tota_all,
        },
        # "item_details": [
        #     {
        #         "id": cart_id,
        #         "price": product_price,
        #         "quantity": qty,
        #         "name": product,
        #         "merchant_name": "Ar-Rasyiid Store"
        #     }
        # ],
        "customer_details":{
            "first_name": order.address.first_name,
            "last_name": order.address.last_name,
            "email": order.address.email,
            "phone": order.address.phone,
            "billing_address": {
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": request.user.phone_number,
                "country_code": "IDN"
                },
            "shipping_address": {
                "first_name": order.address.first_name,
                "last_name": order.address.last_name,
                "email": order.address.email,
                "phone": order.address.phone,
                "address": order.address.address_line_1+', '+ order.address.address_line_2,
                "city": order.address.district.city.name,
                "postal_code": order.address.district.city.post_code,
                "country_code": "IDN"
            },
            "notes": "Thank you for your purchase. Please follow the instructions to pay."
        },
        "enabled_payments": [
                "credit_card", 
                "mandiri_clickpay", 
                "cimb_clicks",
                "bca_klikbca", 
                "bca_klikpay", 
                "bri_epay", 
                "echannel", 
                "indosat_dompetku",
                "mandiri_ecash", 
                "permata_va", 
                "bca_va", 
                "bni_va",
                "bri_va",
                "other_va", 
                "gopay",
                "kioson", 
                "indomaret", 
                "gci", 
                "danamon_online",
                "Indomaret",
                "alfamart",
                "akulaku"
            ],
        "credit_card": {
            "secure": True,
            "installment": {
                "required": True,
                "terms": {
                    "bca": [3,6,12],
                    "bni": [3,6,12],
                    "mandiri": [3,6,12],
                    "cimb": [3,6,12],
                    "bri": [3,6,12],
                    "maybank": [3,6,12],
                    "mega": [3,6,12],
                    "offline": [6, 12]
                }
            },
            "whitelist_bins": [
                "48111111",
                "41111111"
            ]
        },
        "bca_va": {
            "va_number": "12345678911",
            # "free_text": {
            #     "inquiry": [
            #         {
            #             "en": "text in English",
            #             "id": "text in Bahasa Indonesia"
            #         }
            #     ],
            #     "payment": [
            #         {
            #             "en": "text in English",
            #             "id": "text in Bahasa Indonesia"
            #         }
            #     ]
            # }
        },
        "bni_va": {
            "va_number": "12345678"
        },
        "bri_va": {
            "va_number": "12345678"
        },
        "permata_va": {
            "va_number": "1234567890",
            "recipient_name": "MHD DANNY"
        },
        "echannel" : {
            "bill_info1" : "Payment For:",
            "bill_info2" : "debt",
            "bill_key" : "085272330324"
        },
        "callbacks": {
            "finish": "http://127.0.0.1:8000/orders/my_orders//"
        },
        "expiry": {
            "unit": "minute",
            "duration": 1440
        },
        "custom_field1": "Selamat Data di Toko Ar-Rasiid",
        "custom_field2": "Silahkan Melakukan Pembayaran pada waktu yang telah di tentutkan",
        "custom_field3": "Terimakasih"
        }
    err = None
    try:
        transaction = MIDTRANS_SNAP.create_transaction(param)
        transaction_token = transaction['token']
        transaction = transaction_token   
        data = {
            'data': transaction
        }
        return JsonResponse(data)
    except Exception as e:
        err = str(e)
        data = {
            'error': err
        }
        return JsonResponse(data, status=400)

@login_required(login_url='login')
def payments(request):
    body = json.loads(request.body)
    current_user=request.user

    if not current_user.is_authenticated:
        return redirect('login')
    
    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
    # Cek Order object
    if not order:
        return JsonResponse(data = {'error': 'Invalid Order ID'}, status=400)

    # Store transaction details inside Payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order 
    cart_items = CartItem.objects.filter(user=current_user, is_active=True)
    # cek cart items
    if not cart_items:
        return JsonResponse(data = {'error': 'Cart is empty'}, status=400)

    for item in cart_items:
        p = ProductItem.objects.get(id__exact=item.product.id)
        prod = float(p.price)
        IDProduct = p.id # product_item ID
        product_price = prod # product_item price 

        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = IDProduct
        orderproduct.quantity = item.quantity
        orderproduct.product_price = product_price
        orderproduct.ordered = True
        orderproduct.save()

        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variation.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()
        
        # reduce the quantiry of the sold product
        product = ProductItem.objects.get(id=IDProduct)
        product.stock -= item.quantity
        product.save()

    # clarn cart
    CartItem.objects.filter(user=request.user).delete()

    # send ordered receiverd email to customer
    mail_subject = 'Thanks you for your order !'
    message = render_to_string('orders/order_vertification_email.html', {
        'user' : request.user,
        'order': order,
    })
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    #send order number and transaction id back to send data method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID': payment.payment_id
    }
    return JsonResponse(data)

@login_required(login_url='login')
def place_order(request, total=0, quantity=0):
    if not request.user.is_authenticated:
        return redirect('login')
    try:
        current_user = request.user
        cart_items = CartItem.objects.filter(user=current_user, is_active=True)
        cart_count = cart_items.count()
        
        if cart_count <= 0:
            return redirect('store')

        grand_total = 0
        tax = 0
        all_total = 0
        
        for cart_item in cart_items:
            # print('cart_item :', cart_item)
            item = ProductItem.objects.get(id__exact=cart_item.product.id)
            #cek item is not in cart
            if item.stock < cart_item.quantity:
                messages.error(request,f'We only have {item.stock} {cart_item.product.name} left in stock.')
                return redirect('cart')
            # calculate total price
            total += (cart_item.product.price * cart_item.quantity)
            quantity +=cart_item.quantity  
            cardID = cart_item.id

        tax = (2 * total)/100
        grand_total = total + tax

        client_key = settings.MIDTRANS['CLIENT_KEY']
        server_key = settings.MIDTRANS['SERVER_KEY'] 
        server_key = "Basic "+server_key+":"
        server_key_byte = server_key.encode("ascii")
        base64_string = base64.b64encode(server_key_byte)
        server= base64_string.decode("ascii")

        # print('server', server)
        if request.method == 'POST':
            # print ('Request :', request.POST)
            address_id = request.POST['address_id']
            total_weight = request.POST['total_weight']
            courier = request.POST['courier_company']
            cost = request.POST['courier_service']
            node = request.POST['order_note']
            
            all_total = grand_total + int(cost)
            # print('dis', total_weight)
            address = Address.objects.get(id=address_id)
            #cek Address
            if not address:
                messages.error(request,'Data Address not found')
                return redirect('checkout')
            #Cek courier service
            if not courier and not cost:
                messages.error(request,'Data Courier Service not found')
                return redirect('checkout')

            #store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.address = address   
            data.order_note = node
            data.order_total = all_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
                # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #2023020401
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
                
            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)  
            
            if not order:
                messages.error(request,'Data Order not found')
                return redirect('checkout')
            
            #Create Delivery Order 
            delivery = OrderDelivery()
            delivery.order_id = order.id
            delivery.courier = courier
            delivery.cost = cost
            delivery.total_weight = total_weight
            delivery.save()

            context = {
                    'order': order,
                    'cart_items': cart_items,
                    'tax': tax,
                    'cost': cost,
                    'total': total,
                    'all_total': all_total,
                    'client': client_key,
                    'server': server,
                    'cardID': cardID,
            }
                
            return render(request, 'orders/payments.html', context)

    except Exception as e:
        print(f'Error: {e}')
        messages.error(request, 'Data dont valid')
        return redirect('checkout')

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        tax = float(order.tax)
        delivery = float(order.orderdelivery.cost)
        ordered_product = OrderProduct.objects.filter(order_id=order.id)
        subtotal = 0
        total = 0
        for i in ordered_product:
            subtotal += i.product.price * i.quantity
            total += subtotal + order.orderdelivery.cost

        payment = Payment.objects.get(payment_id=transID)

        status_response = MIDTRANS_CORE.transactions.status(str(order_number)) 
        status = status_response['transaction_status']
        print('status', status)
        
        context = {
            'order': order,
            'tax': tax,
            'delivery': delivery,
            'ordered_product': ordered_product,
            'payment': payment,
            'subtotal': subtotal,
            'status': status,
            'status_response': status_response,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')

@csrf_exempt 
def midtrants_callback(request):
    #Get request parameters
    payload = json.loads(request.body)
    # print('payload:', payload)
    order_id = payload['order_id']
    status_code = payload['status_code']
    transaction_status = payload['transaction_status']
    gross_amount = payload['gross_amount']
    signature_rek = payload['signature_key']
    # signature_key = "your_signature_key" # replace with your signature key

    # Check the integrity of the request by comparing the calculated signature with the received signature_key
    # If they match, the request is from MIDtrans and can be trusted.
    # If they don't match, the request might be fake or tampered with.
    # The signature_key is available in your MIDtrans dashboard under API Keys.

    # Calculate the signature using the received order_id, status_code, gross_amount, and server_key
    serverKey = settings.MIDTRANS['SERVER_KEY'] # replace with your server key
    key = order_id+status_code+gross_amount+serverKey
    signature = hashlib.sha512(key.encode('utf8'))

    # cek is signature
    if signature != signature_rek:
        return JsonResponse({
            'message': 'Invalid signature',
            'code': status_code # 401
            })

    order = Order.objects.get(order_number=order_id) # Order
    # cek is order number
    if not order:
        return JsonResponse(
            {
                'message': 'Invalid order',
                'code': status_code # 404
        })

    # Update the order status
    # if transaction_status == 'capture' or transaction_status == 'settlement':
    #     order.status = 'CONFIRM'
    #     order.save()
    
    if transaction_status == 'failure' or transaction_status == 'deny' or transaction_status == 'expire':
        order.status = 'CANCELLED'
        order.save()
        # Update the order status to CANCELLED and redirect to the cancelled page with order details.
        # return redirect('order_cancelled', order_number=order.order_number)

    payment = Payment.objects.get(payment_id=payload['payment_id'])
    payment.status = transaction_status
    payment.save()

    return JsonResponse({
        'code': status_code,
        'message': 'message successfully'
    })

@login_required(login_url='login')
def batal_order(request, order_id):
    try:
        order = Order.objects.get(user=request.user, order_number=order_id)
        status_paymen_midtrans = MIDTRANS_CORE.transactions.status(str(order.order_number)) #get status paymen midtrans
        if status_paymen_midtrans['transaction_status'] == 'pending' or status_paymen_midtrans['transaction_status'] == 'capture':
            #Updata status  Midtrans
            url = "https://api.sandbox.midtrans.com/v2/"+order.order_number+"/cancel"
            print(url)
            headers = {
                "accept": "application/json",
                "Authorization": "Basic " + base64.b64encode((settings.MIDTRANS['SERVER_KEY'] + ":").encode()).decode(),
                
            }
            response = request.post(url, headers=headers)

            if response.status_code == 200:
                order.status = 'CANCELLED'
                order.save()

                #Updata Product Quantity
                for order_product in order.orderproduct_set.all(): #loop orderPorduct
                    order_pro_id = order_product.id  #Get Order Product Id
                    product_id = order_product.product.id #Get Product Id
                    quantity = order_product.quantity #Get Product Qunatity

                    #Updata Product Quantity
                    product = ProductItem.objects.get(id=product_id) 
                    product.stock += quantity
                    product.save()

                # Updata Payment Tabel
                payment_id = order.payment.id
                payment_id = int(payment_id)
                payment = Payment.objects.get(id=payment_id)
                payment.status = 'cancel'
                payment.save()

                messages.success(request, 'Your canceled has been sucsesfully.')
                return redirect('my_orders')
            elif status_paymen_midtrans['transaction_status'] == 'settlement':
                messages.error(request, 'Please confirm by Seller.')
                return redirect('my_orders')
            else:
                messages.error(request, 'Failed to cancel your order.')
                return redirect('my_orders')

    except Order.ObjectDoesNotExist:
        return render(request, '404.html', context)

@login_required(login_url='login')       
def my_orders(request,):
    # try:
        order_all = Order.objects.filter(user=request.user.id, is_ordered=True).order_by('-created_at')
        for order in order_all:
            number = order.order_number
            # Get status midrants payment
            status = MIDTRANS_CORE.transactions.status(str(number))
            transaction_status = status['transaction_status'] 
            print(transaction_status)   
            payment_id = Payment.objects.get(payment_id=status['transaction_id'])
            # Check transaction status
            if transaction_status == 'cancel' or transaction_status == 'deny' or transaction_status == 'expire':
                # Updata Payment
                payment = payment_id
                payment.status = transaction_status
                payment.save()

                
                # print(order)
                order.payment = payment
                order.status = 'CANCELLED'
                order.save()
                # Loop Order Product Details 
                for order_product in order.orderproduct_set.all(): #loop orderPorduct
                    order_pro_id = order_product.id  #Get Order Product Id
                    product_id = order_product.product.id #Get Product Id
                    quantity = order_product.quantity #Get Product Qunatity

                    #Updata Product Quantity
                    product = ProductItem.objects.get(id=product_id) 
                    product.stock += quantity
                    product.save()

            elif transaction_status == 'settlement':
                #update paymen status
                payment = payment_id
                payment.status = transaction_status
                payment.save()


        orders = Order.objects.filter(user=request.user, is_ordered=True, payment__status='settlement').filter(Q(status='CONFIRM') | Q(status='PENDING',)).order_by('-created_at')
        print('o :', orders)
        context = {
            'orders': orders,
            'title': 'My-Order Confirm',
        }
        return render(request, 'orders/my_order/my_order.html', context)
    # except Order.ObjectDoesNotExist:
    #     return render(request, '404.html')

@login_required(login_url='login')
def status_pending(request):
    try:
        orders = Order.objects.filter(user=request.user, is_ordered=True, status='PENDING', payment__status='pending').order_by('-created_at')
            
        context = {
            'orders': orders
        }
        return render(request, 'orders/my_order/pending.html', context)

    except Order.ObjectDoesNotExist:
        return render(request, '404.html', context)

def status_on_the_way(request):
    try:
        orders = Order.objects.filter(user=request.user, is_ordered=True, status='ON_THE_WAY', payment__status='settlement').order_by('-created_at')
        context = {
            'orders': orders,
            'title': 'My-Order On The Way',
        }
        return render(request, 'orders/my_order/my_order.html', context)

    except Order.ObjectDoesNotExist:
        return render(request, '404.html', context)

@login_required(login_url='login')
def status_delivered(request):
    # try:
        orders = Order.objects.filter(user=request.user.id, is_ordered=True, payment__status='settlement').filter(Q(status='COMPLETED') | Q(status='DELIVERED') ).order_by('-created_at')
        
        # Get The Rating reviews
        reviews = ReviewRating.objects.filter(user=request.user, status=True)
        context = {
            'orders': orders,
            'reviews': reviews,
            'title': 'My-Orders Completed',
        }
        return render(request, 'orders/my_order/my_order.html', context)

    # except Order.ObjectDoesNotExist:
    #     return render(request, '404.html', context)

@login_required(login_url='login')
def status_cencelled(request):
    try:
        orders = Order.objects.filter(user=request.user.id, status='CANCELLED', payment__status='cancel').order_by('-created_at')
    
    except Order.ObjectDoesNotExist:
        return render(request, '404.html', context)

    context = {
        'orders': orders,
        'title': 'My-Orders Cancelled',
    }
    return render(request, 'orders/my_order/my_order.html', context)

@login_required(login_url='login')
def all_order(request):
    # try:
        orders = Order.objects.filter(user=request.user.id, is_ordered=True).order_by('-created_at')
        print('orders :', orders)
        context = {
            'orders': orders,
            'title': 'My-Orders All',
        }
        return render(request, 'orders/my_order/my_order.html', context)
    # except Order.ObjectDoesNotExist:
    #     return render(request, '404.html', context)

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(user=request.user, order_number=order_id)
    tax = float(order.tax)
    delivery = float(order.orderdelivery.cost)
    print('order', order)
    subtotal = 0 
    total = 0 
    for i in order_detail:
        subtotal += (i.product_price * i.quantity)
        qty = i.quantity
        print('qty', qty)
        print('subtotal', subtotal)
        total += subtotal + order.orderdelivery.cost

    status = MIDTRANS_CORE.transactions.status(str(order.order_number))
    print('status', status)
    transaction_status = status['transaction_status']    
    payment_id = status['transaction_id']
    payment = Payment.objects.get(payment_id=payment_id)

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
        'total': total,
        'status': transaction_status,
        'status_response':status,
        'tax': tax,
        'delivery': delivery,
        'payment': payment
    }

    return render(request, 'orders/my_order/order_detail.html', context)

@login_required(login_url='login')
def my_transaction(request):
    transaction_list = Order.objects.filter(user=request.user.id, is_ordered=True, payment__status='settlement').order_by('-created_at')
    for order in transaction_list:
        p = order.order_number
        print('trans', p)
        status = MIDTRANS_CORE.transactions.status(str(p))
    # transaction_status = status['transaction_status']
    page = request.GET.get('page', 1)
    paginator = Paginator(transaction_list, 10)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
        
    context = {
        'orders': orders,
        # 'status': transaction_status
    }
    return render(request, 'orders/my_transaction/index.html', context)

@login_required(login_url='login')
def transaction_detail(request, number):
    try:
        curen_user = request.user
        if not curen_user.is_authenticated:
            return redirect('login')
        
        order = Order.objects.filter(user=curen_user, order_number=number, payment__status='settlement').order_by('-created_at')
        
        if not order:
            return redirect('my_transaction')

        context = {
            'order': order
        }
        return render(request, 'orders/my_transaction/detail.html', context)
    
    except Order.DoesNotExist:
        return render(request, '404.html')
    
def get_review(request, order_id):
    order = Order.objects.filter(order_number=order_id, user=request.user.id, is_ordered=True).order_by('-created_at')
    
    if not order:
        return redirect('my_orders')

    context = {
        'order': order,
        'title': 'Review'
        }

    return render(request, 'orders/my_order/reviews/product_review.html', context)

def submit_review(request,  item_id):
    url = request.META.get('HTTP_REFERER')
    orderproduct = get_object_or_404(OrderProduct, id=item_id)
    print('products :', orderproduct.product.id)
    
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user=request.user.id, item__id=orderproduct.product.id)
            print('review : ', reviews)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect('get_review', orderproduct.order.order_number)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.item_id = orderproduct.product.id
                data.product_id = orderproduct.product.product.id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect('get_review', orderproduct.order.order_number)
            else:
                messages.error(request, 'Review submission failed.')
                return redirect(url)
    
    context = {
        'orderproduct': orderproduct,
    }

    return render(request, 'orders/my_order/reviews/create_review.html', context)

@login_required(login_url='login')
def order_accept(request, order_id):
    order = Order.objects.get(order_number=order_id, user=request.user.id)
    
    if not order:
        return redirect('my_orders')
    
    order.status = 'COMPLETED'
    order.save()
    return redirect('get_review', order.order_number)