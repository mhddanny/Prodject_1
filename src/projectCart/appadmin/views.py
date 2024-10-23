from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.utils.text import slugify
# import django os setting.
from django.conf import settings


from carts.models import CartItem
from category.models import Category
from store.models import Product, ProductItem, ProductPaket, ProductGallery, ViewCount, Variation
from orders.models import Order, OrderProduct, Payment
from profiles.models import Account, UserProfile
from blog.models import Post

from django.forms import modelformset_factory

from . forms import UserForm, UserProfileForm, Account
from . forms import ProductForm, ProductItemForm, ProductPaketForm, ProductGaleryForm, UserCategoryForm

import datetime
import json
import os


@login_required
def dashboard_admin(request):
    #check user is logged in
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')

    # # Get the total number of products
    # product_count = Product.objects.count()

    # # Get the total number of posts
    # post_count = Post.objects.count()

    amount = 0
    carts = 0
    customers = 0
    payment = 0
    payment_two = 0

    
    customers = Account.object.filter(is_active=True, is_admin=False, is_staff=False).count() # Get the total number of users

    todays_date = datetime.date.today() #hari ini
    yesterdays_date = todays_date-datetime.timedelta(days=1) # kemarin
    last_mount_ago = todays_date-datetime.timedelta(days=30) #perhitungan 30 hari
    two_amount_ago = todays_date-datetime.timedelta(days=60) # perhitungan 60 hari
    
    carts_today = CartItem.objects.filter(is_active=True, created_date__gte=todays_date) # Get cart items today
    carts_yesterday = CartItem.objects.filter(is_active=True, created_date__gte=yesterdays_date) #Get cart items yesterday

    total_cart_today = carts_today.count() # Total cart items today
    total_cart_yesterday = carts_yesterday.count() # Total cart items yesterday
    # Get percence of total_cart today and total_cart_yesterday
    total_precentse_count_cart = ((total_cart_today - total_cart_yesterday) / total_cart_yesterday if total_cart_yesterday else 0) * 100

    # Get Total Views product today
    product_views = ViewCount.objects.filter(date__gte=todays_date).count()
    product_views_yestesterday = ViewCount.objects.filter(date__gte=yesterdays_date).count()
    total_precentse_count_views = ((product_views - product_views_yestesterday) / product_views if product_views else 0) * 100

    #Get Filter order products for today
    orderProducts = OrderProduct.objects.filter(ordered=True, created_at__gte=todays_date)
    orderProductsYesterday = OrderProduct.objects.filter(ordered=True, created_at__gte=yesterdays_date)
    # Get the total amount of money earned today
    today_earnings = orderProducts.aggregate(Sum('product_price'))
    #Get the total amount of money earned yesterday
    yesterdays_earnings= orderProductsYesterday.aggregate(Sum('product_price'))
    # Get the percentage of today's total money amount and yesterday's total money amount
    todal_percentage_amount = ((today_earnings['product_price__sum'] - yesterdays_earnings['product_price__sum']) / today_earnings['product_price__sum'] if today_earnings['product_price__sum'] else 0 ) * 100 if yesterdays_earnings['product_price__sum'] != 0 else 0  
        
    # # Get the total products sold today
    product_sold_today = orderProducts.count()
    # Get the total products sold yesterdays
    order_count_yesterdays = orderProductsYesterday.count()
    # get precentace order_count_yesterdays in product_sold_today
    total_precentse_count = ((product_sold_today - order_count_yesterdays) / product_sold_today if product_sold_today else 0 ) * 100
        
    # Get the total amount of money earned today 
    for item in orderProducts:
        amount += item.quantity * item.product_price
        

    # Get filter payment settlement for 30 day
    payments = Payment.objects.filter(status="settlement", created_at__gte=last_mount_ago, created_at__lte=todays_date)
    payment_two_ago = Payment.objects.filter(status="settlement", created_at__gte=two_amount_ago, created_at__lte=last_mount_ago)
    # Get the total amount of money earned for 30 day

    for p in payments:
        payment += float(p.amount_paid)

    for p in payment_two_ago:
        payment_two += float(p.amount_paid)

    # precentace payment
    payment_percentace = ((payment - payment_two) / payment if payment else 0 ) * 100 if payment_two != 0 else 0
    print('payment_two_ago :', payment_two_ago)

    context = {
            'carts': total_cart_today,
            'total_precentse_count_cart': round(total_precentse_count_cart),
            'product_views': product_views,
            'customers': customers,
            'order': orderProducts,
            'amount': amount,
            'total_precentse_count_views': round(total_precentse_count_views),
            'todal_percentage_amount': round(todal_percentage_amount),
            'total_precentse_count': round(total_precentse_count),
            'payment_percentace': round(payment_percentace),
            'payment': payment,
            'title': 'Dashboard '
        }

    return render (request, 'appadmin/index.html', context)

@login_required
def orders(request):
    # Get the order product
    orders = Order.objects.filter(is_ordered=True).order_by('-created_at').all()
    # Set paging parameters
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)

    # Get the total number of orders
    total_orders = orders.count()
    order_pending = orders.filter(status="PENDING").count()
    order_confirm = orders.filter(status="CONFIRM").count()
    order_cancelled = orders.filter(status="CANCELLED").count()
    order_completed = orders.filter(status="COMPLETED").count()
    order_otw = orders.filter(status="ON_THE_WAY").count()
    order_delivered = orders.filter(status="DELIVERED").count()


    context = {
        'orders': paged_orders,
        'total_orders': total_orders,
        'pending': order_pending,
        'confirm': order_confirm,
        'cancelled': order_cancelled,
        'completed': order_completed,
        'otw' :order_otw,
        'delivered' :order_delivered,
        'title': 'Orders',
    }

    return render(request, 'appadmin/orders/index.html', context)

@login_required
def orders_pending(request):
    # Get the order product
    orders_all = Order.objects.filter(is_ordered=True).order_by('-created_at').all()
    orders = orders_all.filter(status='PENDING').order_by('-created_at').all()
    # Set paging parameters
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)

    # Get the total number of orders
    total_orders = orders_all.count()
    order_pending = orders_all.filter(status="PENDING").count()
    order_confirm = orders_all.filter(status="CONFIRM").count()
    order_cancelled = orders_all.filter(status="CANCELLED").count()
    order_completed = orders_all.filter(status="COMPLETED").count()
    order_otw = orders_all.filter(status="ON_THE_WAY").count()
    order_delivered = orders_all.filter(status="DELIVERED").count()

    context = {
        'orders': paged_orders,
        'total_orders': total_orders,
        'pending': order_pending,
        'confirm': order_confirm,
        'cancelled': order_cancelled,
        'completed': order_completed,
        'otw' :order_otw,
        'delivered' :order_delivered,
        'title': 'Orders Pending',
    }
    return render(request, 'appadmin/orders/index.html', context)

@login_required
def orders_confirm(request):
    # Get the order product
    orders_all = Order.objects.filter(is_ordered=True).order_by('-created_at').all()
    orders = orders_all.filter(status='CONFIRM', payment__status='settlement').order_by('-created_at').all()
    # Set paging parameters
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)

    # Get the total number of orders
    total_orders = orders_all.count()
    order_pending = orders_all.filter(status="PENDING").count()
    order_confirm = orders_all.filter(status="CONFIRM").count()
    order_cancelled = orders_all.filter(status="CANCELLED").count()
    order_completed = orders_all.filter(status="COMPLETED").count()
    order_otw = orders_all.filter(status="ON_THE_WAY").count()
    order_delivered = orders_all.filter(status="DELIVERED").count()

    context = {
        'orders': paged_orders,
        'total_orders': total_orders,
        'pending': order_pending,
        'confirm': order_confirm,
        'cancelled': order_cancelled,
        'completed': order_completed,
        'otw' :order_otw,
        'delivered' :order_delivered,
    }
    return render(request, 'appadmin/orders/index.html', context)

@login_required
def orders_otw(request):
    # Get the order product
    orders_all = Order.objects.filter(is_ordered=True).order_by('-created_at').all()
    orders = orders_all.filter(is_ordered=True, status='ON_THE_WAY', payment__status='settlement').order_by('-created_at').all()
    # Set paging parameters
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)

    # Get the total number of orders
    total_orders = orders.count()
    order_pending = orders_all.filter(status="PENDING").count()
    order_confirm = orders_all.filter(status="CONFIRM").count()
    order_cancelled = orders_all.filter(status="CANCELLED").count()
    order_completed = orders_all.filter(status="COMPLETED").count()
    order_otw = orders_all.filter(status="ON_THE_WAY").count()
    order_delivered = orders_all.filter(status="DELIVERED").count()

    context = {
        'orders': paged_orders,
        'total_orders': total_orders,
        'pending': order_pending,
        'confirm': order_confirm,
        'cancelled': order_cancelled,
        'completed': order_completed,
        'otw' :order_otw,
        'delivered' :order_delivered,
    }
    return render(request, 'appadmin/orders/index.html', context)

@login_required
def orders_delivered(request):
    # Get the order product
    orders_all = Order.objects.filter(is_ordered=True).order_by('-created_at').all()
    orders = orders_all.filter(is_ordered=True, status='DELIVERED', payment__status='settlement').order_by('-created_at').all()
    # Set paging parameters
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)

    # Get the total number of orders
    total_orders = orders.count()
    order_pending = orders_all.filter(status="PENDING").count()
    order_confirm = orders_all.filter(status="CONFIRM").count()
    order_cancelled = orders_all.filter(status="CANCELLED").count()
    order_completed = orders_all.filter(status="COMPLETED").count()
    order_otw = orders_all.filter(status="ON_THE_WAY").count()
    order_delivered = orders_all.filter(status="DELIVERED").count()

    context = {
        'orders': paged_orders,
        'total_orders': total_orders,
        'pending': order_pending,
        'confirm': order_confirm,
        'cancelled': order_cancelled,
        'completed': order_completed,
        'otw' :order_otw,
        'delivered' :order_delivered,
    }
    return render(request, 'appadmin/orders/index.html', context)

@login_required
def orders_batal(request):
    # Get the order product
    orders_all = Order.objects.filter(is_ordered=True).order_by('-created_at').all()
    orders = orders_all.filter(is_ordered=True, status='CANCELLED').order_by('-created_at').all()
    # Set paging parameters
    paginator = Paginator(orders, 5)
    page = request.GET.get('page')
    paged_orders = paginator.get_page(page)

    # Get the total number of orders
    total_orders = orders.count()
    order_pending = orders_all.filter(status="PENDING").count()
    order_confirm = orders_all.filter(status="CONFIRM").count()
    order_cancelled = orders_all.filter(status="CANCELLED").count()
    order_completed = orders_all.filter(status="COMPLETED").count()
    order_otw = orders_all.filter(status="ON_THE_WAY").count()
    order_delivered = orders_all.filter(status="DELIVERED").count()

    context = {
        'orders': paged_orders,
        'total_orders': total_orders,
        'pending': order_pending,
        'confirm': order_confirm,
        'cancelled': order_cancelled,
        'completed': order_completed,
        'otw' :order_otw,
        'delivered' :order_delivered,
    }
    return render(request, 'appadmin/orders/index.html', context)

@login_required
def orderDetail(request, order_id):
    try:
        # Get authenticated user
        user = request.user

        # Check if the user is authenticated and is an admin
        if not user.is_authenticated or not user.is_admin:
            return redirect('login')

        # Get the order
        order = Order.objects.filter(id=order_id).all()

        context = {
            'order': order,
        }
        return render(request, 'appadmin/orders/detail.html', context)
    except Exception as e:
        print('Error :', e)
        messages.error(request, 'Data not found')
        return redirect('orders')

@login_required
def confirm_order(request, order_id):
    try:
        url = request.META.get('HTTP_REFERER')
        # Get the authenticated user
        user = request.user

        # Check if the user is authenticated and is an admin
        if not user.is_authenticated or not user.is_admin:
            return redirect('login')

        # Get the order
        order = Order.objects.filter(id=order_id).first()

        #check Pyment orde
        if order.payment.status == 'settlement' or order.payment.status == 'capture' :
            # Check Order status CONFIRM
            if order.status == 'PENDING':
                # Update the order status to 'Confirmed'
                order.status = 'CONFIRM'
                order.save()
            else:
                messages.error(request, 'Order status is not CONFIRM...')
                return redirect(url)

        else:
            messages.error(request, 'Payment method is not completed for this order...')
            return redirect(url)

        messages.success(request, 'Order confirmed successfully...')
        return redirect(url)
    except Exception as e:
        print('Error :', e)
        messages.error(request, 'Failed to confirm order...')
        return redirect(url)

@login_required
def ready_to_sent(request, order_id):
    # try:
        url = request.META.get('HTTP_REFERER')
        # Get the authenticated user
        user = request.user

        # Check if the user is authenticated and is an admin
        if not user.is_authenticated or not user.is_admin:
            return redirect(url)

        # Get the order
        order = Order.objects.filter(id=order_id).first()

        #check Pyment orde
        if order.payment.status == 'settlement' or order.payment.status == 'capture' :
            # Check Order status DELIVERY
            if order.status == 'CONFIRM':
                # Update the order status to 'Ready to Send'
                order.status = 'ON_THE_WAY'
                order.save()
            else:
                messages.error(request, 'Order is not On The Way...')
                return redirect(url)

        else:
            messages.error(request, 'Payment method is not completed for this order...')
            return redirect(url)
            
        messages.success(request, 'Order On The Way Success...')
        return redirect(url)
    # except Exception as e:
    #     print('Error :', e)
    #     messages.error(request, 'Failed to update order status')
    #     return redirect(url)

def orderReadyDeliver(request, order_id):
    try:
        # Get the authenticated user
        user = request.user

        # Check if the user is authenticated and is an admin
        if not user.is_authenticated or not user.is_admin:
            return redirect('login')

        # Get the order
        order = Order.objects.filter(id=order_id).first()

        #check Pyment orde
        if order.payment != 'statement' or order.payment != 'capture' :
            messages.error(request, 'Payment method is not supported for this order')
            return redirect('orders')

        # Checko Order status pennding
        if order.status != 'CONFIRM':
            messages.error(request, 'Order is not in pending status')
            return redirect('orders')

        # Update the order status to 'Ready for Delivery'
        order.status = 'ON_THE_WAY'
        order.save()

        messages.success(request, 'Order has been marked as ready for delivery.')
        return redirect('orders')
    except Exception as e:
        print('Error :', e)
        messages.error(request, 'Failed to mark order as ready for delivery.')
        return redirect('orders')

#view category
@login_required
def category(request):
    # context = {}
    #checks category admin settings
    # if CategoryAdminSetting.objects.first().allow_category_management:
    #     context['allow_category_management'] = True
    # else:
    #     context['allow_category_management'] = False

    # Get the authenticated user
    user = request.user

    # Check if the user is authenticated and is an admin
    if not user.is_authenticated or not user.is_staff:
        return redirect('login')

    # Get all categories
    category = Category.objects.order_by('category_name')
    paginator = Paginator(category,3)
    page = request.GET.get('page')
    paged_category = paginator.get_page(page)
    category_count = category.count()
    print(category)

    template = loader.get_template("appadmin/category/index.html")
    context = {
        'category': paged_category, 
        'category_count': category_count,
        'title': 'Category Product'
        }
    
    return HttpResponse(template.render(context, request))

def add_category(request):
    category_form = UserCategoryForm()
    if request.method == 'POST':
        print('request.FILES :', request.FILES)
        print('request.POST :', request.POST)
        if request.FILES:
            image = request.FILES['cat_image']
            video_file = request.FILES['video_file']
        else:
            image = 'images/default.jpg'
            video_file = ''

        # create and save the category
        category_form = UserCategoryForm(request.POST , request.FILES)
        if category_form.is_valid():
            name = request.POST['category_name']
            category = category_form.save(commit=False)
            category.slug = slugify(name)
            category.cat_image = image
            category.video_file = video_file
            category.save()
            
            messages.success(request, 'Categoty has been successfully')
            return redirect('category')
        else:
            messages.error(request, 'Cateory is not valid.')
            return redirect('category')

    context = {
        'title': 'Add',
        'category': category_form,
    }
    return render(request, "appadmin/category/set_category.html", context)

@login_required
def edit_category(request, slug, pk):
    try:
        category_get = get_object_or_404(Category, slug=slug, pk=pk)
        # print('image :', category_get.cat_image)
        if request.method == 'POST':
                # os.remove(os.path.join(settings.MEDIA_ROOT, category_get.cat_image.path))
                # os.remove(os.path.join(settings.MEDIA_ROOT, category_get.video_file.path))
            category_form = UserCategoryForm(request.POST or None, instance=category_get)  
            if category_form.is_valid():
                # update category
                category_name = category_form.cleaned_data['category_name']
                category = category_form.save(commit=False)
                category.slug = slugify(category_name)
                category.save()

                # update image 
                if request.FILES:
                    for f in request.FILES :
                        # print('file :', f)
                        if f == 'cat_image':
                            image = request.FILES['cat_image']
                            os.remove(os.path.join(settings.MEDIA_ROOT, category_get.cat_image.path))
                            category.cat_image = image
                            category.save()
                            
                        if f == 'video_file':
                            video_file = request.FILES['video_file']
                            os.remove(os.path.join(settings.MEDIA_ROOT, category_get.video_file.path))
                            category.video_file = video_file
                            category.save()

                messages.success(request, 'Category update successfully.')
                return redirect('category')
            else:
                messages.error(request, 'Category is not available.')
                category_form = UserCategoryForm(instance=category_get)
                return redirect('edit_category', slug=slug, pk=pk)

        else:
            category_form = UserCategoryForm(instance=category_get)

        context = {
            'title': 'Edit',
            'category': category_form,
            'cat' : category_get,
        }
        return render(request, "appadmin/category/set_category.html", context)

    except Category.DoesNotExist:
        raise Http404("Category does not exist")

@login_required
def delete_category(request, slug, pk):
    try:
        # check authentication user
        user = request.user
        if not user.is_authenticated or not user.is_admin:
            return redirect('login')
        
        # get the category by slug and id
        category = Category.objects.get(slug=slug,pk=pk)

        # check if the category has product associated with it
        product = Product.objects.filter(category=category)
        # check product exist in other table
        if product.exists():
            messages.error(request, 'This category has product associated with it. Please delete the product first.')
            return redirect('category')
        
        # delete the category
        category.delete()
        messages.success(request, 'Category has been deleted successfully.')
        return redirect('category')
    except Category.DoesNotExist:
        raise Http404("Category does not exist")

#view product
@login_required
def products(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return redirect('login')

    context = {}
    products = Product.objects.all().order_by('-created_date')
    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()
    
    context = {'products': paged_products, 'product_count': product_count}
        
    return render(request, 'appadmin/product/index.html', context)

@login_required
def add_product(request):
    if request.method == 'POST':
        print(request.POST, request.FILES)
        #print(request.POST.get('varian_category', 'variation_value'))
        product_form = ProductForm(request.POST)
        product_item_form = ProductItemForm(request.POST)
        paket_form = ProductPaketForm(request.POST) 
        galery_product = request.FILES.getlist("galery_product")
        
        price = request.POST.getlist('price')
        stock = request.POST.getlist('stock')
        is_available = request.POST.getlist('is_available')
        is_default = request.POST.getlist('is_default')
        data = [price, stock, is_available, is_default]
        colors = request.POST.getlist('color')
        print('color: %s' % colors)


        sizes = request.POST.getlist('size')

        # Valideate the product form all
        if product_form.is_valid() and product_item_form.is_valid() and paket_form.is_valid() :
            product_image = request.FILES['image_product']
            product_name = request.POST.get('product_name')
            product = product_form.save(commit=False)
            product.slug = slugify(product_name)
            product.images = product_image
            product.save()
            
            #save product item
            
            # item = product_item_form.save(commit=False)
            # item.product = product
            # item.price = request.POST['price']
            # item.stock = request.POST['stock']
            # item.is_available = request.POST['is_available']
            # item.is_default = request.POST['is_default']
            # item.save()

            # save the item to the database
            for i in range(len(data)):
                item = ProductItem.objects.create(product=product, price=price[i], stock=stock[i], is_available=is_available[i])
                for c in colors:
                    Variation.objects.create(product_item=item, varian_category='color', variation_value=c)
                    for s in sizes:
                        Variation.objects.create(product_item=item, varian_category='size', variation_value=s)


            #save paroduct paket
            paket = paket_form.save(commit=False) 
            paket.product = product
            paket.save()

            for i in galery_product:
                ProductGallery.objects.create(product=product, image=i)

            messages.success(request, 'Product has been succesfuly')
            return redirect('products')
        else:
            print(product_form.errors and paket_form.errors )
    else:
        product_form = ProductForm()
        product_item_form = ProductItemForm()
        paket_form = ProductPaketForm()
        item_images = ProductGaleryForm()
        

    context = {
        'title': 'Add',
        'product': product_form,
        'item': product_item_form,
        'paket': paket_form,
        'item_images': item_images,
        
    }
    return render(request, 'appadmin/product/add_product.html', context)


@login_required
def set_product(request):
    if request.method == 'POST':
        print(request.POST, request.FILES)
        #print(request.POST.get('varian_category', 'variation_value'))
        product_item = []
        product_form = ProductForm(request.POST)
        product_item_form = ProductItemForm(request.POST)
        paket_form = ProductPaketForm(request.POST) 
        galery_product = request.FILES.getlist("galery_product")
        
        price = request.POST.getlist('price')
        stock = request.POST.getlist('stock')
        sku = request.POST.getlist('sku')
        is_available = request.POST.getlist('is_available')
        is_default = request.POST.getlist('is_default')
       
        image_colors = request.POST.getlist('image_variant')

        for s in sku:
            split_s = s.split('-')
            print('split_s :', split_s)
            colors = split_s[0]
            sizes = split_s[1]
            

        # Valideate the product form all
        if product_form.is_valid() and product_item_form.is_valid() and paket_form.is_valid() :
            product_image = request.FILES['image_product']
            product_name = request.POST.get('name')
            product = product_form.save(commit=False)
            product.slug = slugify(product_name)
            product.images = product_image
            product.save()

            # save the item to the database
            for i in range(len(price)):
                print("Saving product :", i)
                item = ProductItem.objects.create(product=product, price=price[i], stock=stock[i], sku=sku[i], is_available=is_available[i])
          
                sku_split = item.sku.split('-')
                print('sku_split :', sku_split)
                Variation.objects.create(product_item=item, varian_category='color', variation_value=sku_split[0])
                Variation.objects.create(product_item=item, varian_category='size', variation_value=sku_split[1])

                product_item.append(item)
                print('Product :', product_item)
                #print('Product_item :', product_item[0])
                product_default = product_item[0]
                product_default.is_default = True
                product_default.save()

            #save paroduct paket
            paket = paket_form.save(commit=False) 
            paket.product = product
            paket.save()


            for i in galery_product:
                ProductGallery.objects.create(product=product, image=i)

            messages.success(request, 'Product has been succesfuly')
            return redirect('products')
        else:
            print(product_form.errors and paket_form.errors )
    else:
        product_form = ProductForm()
        product_item_form = ProductItemForm()
        paket_form = ProductPaketForm()
        item_images = ProductGaleryForm()


    context = {
        'title': 'Add',
        'product': product_form,
        'item': product_item_form,
        'paket': paket_form,
        'item_images': item_images,
        
    }
    return render(request, 'appadmin/product/set_product.html', context)

@login_required
def edit_product(request, pk):
    product_get = get_object_or_404(Product, pk=pk)
    product_item = modelformset_factory(ProductItem, form=ProductItemForm, extra=0)
    product_paket = ProductPaket.objects.get(product=product_get)
    ImagesFormSet = modelformset_factory(ProductGallery, form=ProductGaleryForm, extra=1, max_num=5)
    
    if request.method == 'POST':
        product_form = ProductForm(request.POST, request.FILES, instance=product_get)
        product_item_form = ProductItemForm(request.POST, instance=product_item)
        paket_form = ProductPaketForm(request.POST, instance=product_paket)   
        product_images = ImagesFormSet(request.POST or None, request.FILES or None)
        
        if product_form.is_valid() and product_item_form.is_valid() and paket_form.is_valid() and product_images.is_valid():
            product_name = product_form.cleaned_data['name']
            product = product_form.save(commit=False)
            product.slug = slugify(product_name)
            product.save()
            
            #save product item
            item = product_item_form.save(commit=False)
            item.product = product
            item.save()
            #save paroduct paket
            paket = paket_form.save(commit=False) 
            paket.product = product
            paket.save()

            print(product_images.cleaned_data)
            data = ProductGallery.objects.filter(product=product_get)
            for index, i in enumerate(product_images):
                if i.cleaned_data:
                    if i.cleaned_data['id'] is None:
                        photo = ProductGallery(product=product_get, image=i.cleaned_data.get['image'])
                        photo.save()
                    elif i.cleaned_data['image'] is None:
                        photo = ProductGallery(id=request.POST.get('form-' + str(index) + '-id'))
                        photo.delete()
                    else:
                        photo = ProductGallery(product=product_get, image=i.cleaned_data.get['image'])
                        d = ProductGallery.objects.get(id=data[index].id)
                        d.image = photo.image
                        d.save()

            messages.success(request, 'Change has been succesfuly')
            return redirect('products')
        else:
            messages.error(request, 'Change has been Errors')
            product_form = ProductForm(instance=product_get)
            product_item_form = ProductItemForm(instance=product_item)
            paket_form = ProductPaketForm(instance=product_paket)
            product_images = ImagesFormSet(queryset=ProductGallery.objects.filter(product=product_get))
   
    else:
        product_form = ProductForm(instance=product_get)
        product_item_form = product_item(queryset=ProductItem.objects.filter(product=product_get))
        paket_form = ProductPaketForm(instance=product_paket)
        product_images = ImagesFormSet(queryset=ProductGallery.objects.filter(product=product_get))

    context = {
        'title': 'Edit',
        'product': product_form,
        'item': product_item_form,
        'paket': paket_form,
        'product_images': product_images,
    }
    return render(request, 'appadmin/product/edit_product.html', context)

@login_required
def delete_product(request, pk):
    product = Product.objects.get(pk=pk)
    # paket = ProductPaket.objects.get(product=product).delete()
    product.delete()

    messages.success(request, 'Deleted was susccesfully')
    return redirect('products')

@login_required
def get_product_attribute_value_color(request):
    data  = request.GET.get('value')
    attribite_value = ProductAttributeValue.objects.filter(product_attribute=1, attribute_value__icontains=data)
    return JsonResponse([{'id': variation.id, 'value': variation.attribute_value} for variation in attribite_value], safe=False)

@login_required
def post_create_product_attribute_color(request):
    data = request.POST.get('value')
    attribute = ProductAttributeValue.objects.create(product_attribute=1, attribute_value=data)
    return JsonResponse({'id': attribute.id, 'value': attribute.attribute_value}, safe=False)


@login_required
def get_product_attribute_value_size(request):
    data  = request.GET.get('value')
    attribite_value = ProductAttributeValue.objects.filter(product_attribute=2, attribute_value__icontains=data)
    return JsonResponse([{'id': variation.id, 'value': variation.attribute_value} for variation in attribite_value], safe=False)


@login_required
def add_warehouse(request):
    pass

#view payment
@login_required()
def payment_analisis(request):
    todays_date = datetime.date.today() #hari ini
    six_mounth_ago = todays_date-datetime.timedelta(days=30*6) #perhitungan 6 bulan * 30 hari
    payments = Payment.objects.filter( 
            created_at__gte=six_mounth_ago, created_at__lte=todays_date) #fileter payment 6 bulan terakir, dan perhari
    
    finalrep = {}
    
    #menampilkan data payment berdasarkan
    def get_status(payment):
        return payment.status

    status_list = list(set(map(get_status, payments))) #megambil semua data status tampa duplikat

    # mengambil data amount dari tpayment
    def get_payment_status_amount(status):
        amount = 0
        filtered_by_status = payments.filter(status=status)
        # loop amount_paid
        for item in filtered_by_status:
            amount = item.amount_paid
        return amount

    for x in payments: #loop payment
        for y in status_list: #loop satatus list
            finalrep[y] = get_payment_status_amount(y)

    return JsonResponse({'payment_status_data': finalrep}, safe=False)
    
#view analytics
@login_required
def analisis(request):
    product_views = 0
    order = 0
    amount = 0

    todays_date = datetime.date.today() #hari ini
    last_mount_ago = todays_date-datetime.timedelta(days=30)
    six_mount_ago = todays_date-datetime.timedelta(days=30*6) #perhitungan 6 bulan * 30 hari

    product_views = ViewCount.objects.filter(date__range =[last_mount_ago, todays_date])
    orderProducts = OrderProduct.objects.all().filter(ordered=True,created_at__gte=todays_date)
    for item in orderProducts:
        amount += item.product_price
        # amount = [sum(amount)]
        
    order = orderProducts
    print('amount',amount)
    conntext = {
        'amount': amount,
        'order': order,
        'product_views': product_views,
    }

    return render(request, 'appadmin/analisis/index.html', conntext)

@login_required
def profile(request):

    if not request.user.is_authenticated or not request.user.is_staff :
        return redirect('home')

    userprofile = get_object_or_404(UserProfile, user=request.user)
    admin = UserProfile.objects.all().filter(user__is_admin="True", user__is_active="True")[:1]
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()

            profile_form.save(commit=False)
            profile_form.profile_picture = request.POST.get('profile_picture', None)
            profile_form.save()
            
            messages.success(request, 'Your profile has been update')
            return redirect('profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)

    context = {
        'admin': admin,
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile
    }
    return render (request, 'appadmin/profile/profile_edit.html', context)

@login_required
def customers(request):

    customer = UserProfile.objects.all().filter(user__is_admin="False", user__is_active="True")[:4]
    context = {
        'customer': customer
    }

    return render(request, 'appadmin/customer/index.html', context)