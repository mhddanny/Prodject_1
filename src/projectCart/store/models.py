from django.conf import settings
from django.db import models
from django.db.models import Avg, Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from category.models import Category
from django_ckeditor_5.fields import CKEditor5Field
from profiles.models import Account
import uuid

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    category = models.ForeignKey(Category, on_delete=models.RESTRICT)
    description = models.TextField(max_length=250, blank=True)
    long_description = CKEditor5Field(blank=True, null=True, config_name='extends')
    images = models.ImageField(upload_to='photos/products', default='images/default.png')
    is_available = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modifield_date = models.DateTimeField(auto_now=True)
    users_wislist = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="user_wislish", blank=True)

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        self.images.delete()
        super(Product, self).delete(*args, **kwargs)

    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
    
    def get_price(self):
        product_item = self.productitem_set.get(is_available=True, is_default=True)
        price = product_item.price
        return price
    
    def get_total_stock(self):
        total_stock = 0
        for item in self.productitem_set.all():
            total_stock += item.stock
        return total_stock

    def avrageReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self, status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
                count = int(reviews['count'])
        return count

# Create your models here.
class ProductItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    sku = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
    )
    price = models.IntegerField()
    stock = models.IntegerField()
    
    is_available = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modifield_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.product.name}' "("+ f'{self.sku}'")"

    def get_price(self):
        return self.price

class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager, self).filter(varian_category='color', is_active=True)

    def sizes(self):
        return super(VariationManager, self).filter(varian_category='size', is_active=True)

variation_category_choices = (
    ('color', 'color'),
    ('size', 'size'),
)

class Variation(models.Model):
    product_item = models.ForeignKey(ProductItem, on_delete=models.RESTRICT)
    varian_category = models.CharField(max_length=100, choices=variation_category_choices)
    image_variant = models.ImageField(upload_to='photos/products/variant', default='images/default.png')
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now=True)

    objects = VariationManager()

    def __str__(self):
        return self.variation_value

class ProductGallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)    
    image = models.ImageField(upload_to='photos/products/gallery', blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = 'product Gallery'
        verbose_name_plural = 'product Gallery'  

    def image_tag(self):
        if self.image.url is not None:
            return mark_safe('<img src="{}" height="50"/>'.format(self.image.url))
        else:
            return ""
        
    def delete(self, *args, **kwargs):
        self.image.delete()
        return super(ProductGallery, self).delete(*args, **kwargs)

class ProductPaket(models.Model):    
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    weight = models.IntegerField(blank=True)
    length = models.IntegerField(blank=True)
    width = models.IntegerField(blank=True)
    height = models.IntegerField(blank=True)

    def __str__(self):
        return self.product.name
    
    class Meta:
        verbose_name = 'Product Paket'
        verbose_name_plural = 'Product Paket'


class ReviewRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    item = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    review = models.TextField(max_length=500, blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject

    def averageReviewall(self):
        reviews = ReviewRating.objects.all().aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg

class ViewCount(models.Model):
    product = models.ForeignKey(Product, related_name="product_views",on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=50)
    session = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ip_address


