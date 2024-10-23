from django.db import models
from profiles.models import Address, Account, District
from store.models import ProductItem, Variation
from django.utils.timezone import now
# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    payment_type = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id

class Order(models.Model):
    STATUS = {
        ('PENDING', 'PENDING'),
        ('CANCELLED', 'CANCELLED'),
        ('CONFIRM', 'CONFIRM'),
        ('ON_THE_WAY', 'ON THE_WAY'),
        ('DELIVERED', 'DELIVERED'),
        ('COMPLETED', 'COMPLETED'),
    }
    
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20)
    order_note = models.CharField(max_length=150, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS, default='PENDING')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modifield_date = models.DateTimeField(auto_now=True)

    # Get SUM Total Order Product models
    def get_sum_total(self):
        return sum(op.product_price * op.quantity for op in self.orderproduct_set.all())

    # Get SUM Total Order Product models quantity
    def get_sum_total_quantity(self):
        return sum(op.quantity for op in self.orderproduct_set.all())
        

    def __str__(self):
        return self.order_number

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation, blank=True)
    quantity = models.IntegerField()
    product_price = models.DecimalField(max_digits=9,decimal_places=2)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modifield_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.order.order_number

class OrderDelivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    courier = models.CharField(max_length=150)
    cost = models.IntegerField()
    total_weight = models.IntegerField()

    def __str__(self):
        return self.courier
