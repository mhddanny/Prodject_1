from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from store.models import Product, ProductItem, ReviewRating
from django.db.models import Avg
from category.models import Category

def home (request):
    category = None
    
    products = Product.objects.all().filter(is_available=True).order_by('created_date')[:6]
    # products = Product.objects.prefetch_related('product_item').filter(is_available=True).order_by('created_date')[:6]

    # Descending Order
    new_product = Product.objects.all().filter(is_available=True).order_by('-created_date')[:3]

    #category publis
    publish = Category.objects.filter(is_publish=True)

    #category slide
    category = Category.objects.filter(level=0)


    # Get The reviews
    reviews = None
    productitem = ProductItem.objects.filter(is_available=True)
    for p in productitem:
        reviews = ReviewRating.objects.filter(product_id=p.id, status=True)

    #review_all
    reviewall = ReviewRating.objects.all()

    context = {
        'category': category,
        'publish': publish,
        'products': products,
        'reviews': reviews,
        'reviewall': reviewall,
        'new_product': new_product 
        }
    return render(request, 'home.html', context)


def chat_bubble(request):
    context = {}
    return render(request, 'chat/chat_bubble.html', context)

def about(request):
    context = {}

    return render(request, 'abouts.html', context)

def testimonial(request):
    #review_all
    rating = 0
    reviewall = ReviewRating.objects.all()
    reviews = reviewall.aggregate(average=Avg("rating"))

    if reviews['average'] is not None:
        rating = float(reviews['average'])
    
    context = {
        'rating': rating,
        'reviewall': reviewall,
    }

    return render(request, 'testimonial.html', context)

def blog(request):
    context = {
        
    }
    return render(request, 'blogs/index.html', context)