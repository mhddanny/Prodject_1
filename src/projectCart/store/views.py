from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from category.models import Category
from carts.views import _cart_id
from carts.models import CartItem
from . models import Product, ProductItem, ReviewRating, ProductGallery, ViewCount, Variation
from . forms import ReviewForm
from orders.models import OrderProduct
from django.db.models import Sum

# Create your views here.
def store(request, category_slug=None, size=None, popularity=None, product=None):
    print('requ :', request.GET)
    categories = None
    products = None
    
    size = request.GET.get('size')
    product = request.GET.get('product')
    
    categories = Category.objects.all()
    sizes = Variation.objects.filter(varian_category='size').distinct().values("variation_value").all()
    view = ViewCount.objects.all().count()

    if category_slug !=None:
        #categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(is_available=True,
            category__in=Category.objects.get(slug=category_slug).get_descendants(include_self=True)).order_by('created_date') 
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
            
        try : 
            paged_products = paginator.get_page(page)
        except PageNotAnInteger:
            paged_products = paginator.get_page(1)
        except EmptyPage:
            paged_products = paginator.get_page(paginator.num_pages)
            
        product_count = products.count()     

    elif size != None:
        var = Variation.objects.filter(varian_category='size', variation_value__iexact=size).distinct().values("product_item__product").all()
        print('variation : ', var)
        products = Product.objects.order_by('created_date').filter(is_available=True,
            category__in=Category.objects.all(),
            productitem__in=ProductItem.objects.filter(is_available=True, variation__varian_category='size', variation__variation_value__iexact=size),
            ).distinct()
        
        paged_products = products    
        product_count = products.count()

    elif product == 'pop':
        products = Product.objects.filter(is_available=True,
            product_views__in=ViewCount.objects.all(),
            productitem__in=ProductItem.objects.filter(is_available=True, is_default=True)).order_by('product_views__date')
        print('Products high:', products)
        
        paginator = Paginator(products, 3)
        page = request.GET.get('page')
            
        try : 
            paged_products = paginator.get_page(page)
        except PageNotAnInteger:
            paged_products = paginator.get_page(1)
        except EmptyPage:
            paged_products = paginator.get_page(paginator.num_pages)
            
        product_count = products.count()        

    elif product == 'asc' :
        products = Product.objects.filter(is_available=True,
            productitem__in=ProductItem.objects.filter(is_available=True, is_default=True)).order_by('productitem__price')
        print('Products asc:', products.values('productitem__price'))
        paged_products = products  
        product_count = products.count()
        
    elif product == 'dsc' :
        products = Product.objects.filter(is_available=True,
        productitem__in=ProductItem.objects.filter(is_available=True, is_default=True)).order_by('-productitem__price')
        paged_products = products 
        product_count = products.count()        

    else:
        products = Product.objects.all().filter(is_available=True).order_by('created_date') 
        paginator = Paginator(products, 9)
        page = request.GET.get('page')
            
        try : 
            paged_products = paginator.get_page(page)
        except PageNotAnInteger:
            paged_products = paginator.get_page(1)
        except EmptyPage:
            paged_products = paginator.get_page(paginator.num_pages)
            
        product_count = products.count()
    
    context = {
            'products': paged_products, 
            'product_count': product_count, 
            'categories': categories,
            'sizes': sizes,
            'size': sizes,
            }
        
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        products = Product.objects.all().filter(category__slug=category_slug).order_by('created_date')[:4]
        #Get The Product Gallery
        product_gallery = ProductGallery.objects.filter(product=single_product)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product__product=single_product).exists()
        variants = Variation.objects.filter(product_item__product=single_product).distinct().values("varian_category" ,"variation_value")
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            # orderproduct = OrderProduct.objects.filter(user=request.user.id, product_id=single_product.productitem_set.get()).exists()
            orderproduct = OrderProduct.objects.filter(user=request.user.id, ordered=True ).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None 
    else:
        orderproduct = None

    # OrderProduct
    quantityAll = OrderProduct.objects.filter(product=single_product.id).aggregate(s=Sum('quantity'))['s']

    # Get The Rating reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    

    #Get the check ip client review
    ip=request.META['REMOTE_ADDR']
    if not ViewCount.objects.filter(product=single_product, session=request.session.session_key):
        view = ViewCount(product=single_product, ip_address=ip, session=request.session.session_key)
        view.save()

    #Get the reviews product
    product_view = ViewCount.objects.filter(product=single_product).count()

    context = {
        'single_product': single_product,
        'in_cart' : in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
        'products': products,
        'quantityAll': quantityAll,
        'product_view': product_view,
        'variants': variants,
        }

    return render(request, 'store/product_detail.html', context)

def get_sizes_api(request):
    if request.method == 'GET':
        print('request :', request.GET)
        size = []
        variation = request.GET.get('color')
        # print('color :', variation)
        product_id = request.GET.get('item_id')
        # print('product_id :', product_id)
        products = ProductItem.objects.filter(product=product_id, variation__variation_value=variation)
        for product in products:
            productId = product.id
            variations = list(Variation.objects.filter(product_item=productId, varian_category='size').values('variation_value'))
            # print('sizes :', variations)

            size += list(variations)
            # print('size :', size)
        
        data = dict()
        data = {
            'data': size
        }
        return JsonResponse(data)

def get_price_item_api(request, **kwargs):
    if request.method == 'GET':
        item = []
        product_id = request.GET.get('item_id')
        # print('product_id = %s' % product_id)
        color = request.GET.get('color')
        size = request.GET.get('size')
        price = ProductItem.objects.filter(product=product_id, variation__variation_value__iexact=color).filter(variation__variation_value__iexact=size)
        # print('Price :', price)
        item = list(price.values())
        # print('Item :', item)
        data = dict()
        data = {
            'data': item,
        }
        
        return JsonResponse(data)

def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        sizes = Variation.objects.filter(varian_category='size').distinct().values("variation_value").all()

        
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(name__icontains=keyword))
            print('Products :', products) 
            product_count = products.count()
            
    categories = Category.objects.all()
    context = {
            'products':products,
            'product_count': product_count,
            'categories': categories,
            'keyword': keyword,
            'sizes': sizes,
        }
    return render(request, 'store/store.html', context)

# def submit_review(request, product_id):
#     url = request.META.get('HTTP_REFERER')
#     if request.method == 'POST':
#         try:
#             reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
#             form = ReviewForm(request.POST, instance=reviews)
#             form.save()
#             messages.success(request, 'Thank you! Your review has been updated.')
#             return redirect(url)
#         except ReviewRating.DoesNotExist:
#             form = ReviewForm(request.POST)
#             if form.is_valid():
#                 data = ReviewRating()
#                 data.subject = form.cleaned_data['subject']
#                 data.rating = form.cleaned_data['rating']
#                 data.review = form.cleaned_data['review']
#                 data.ip = request.META.get('REMOTE_ADDR')
#                 data.product_id = product_id
#                 data.user_id = request.user.id
#                 data.save()
#                 messages.success(request, 'Thank you! Your review has been submitted.')
#                 return redirect(url)