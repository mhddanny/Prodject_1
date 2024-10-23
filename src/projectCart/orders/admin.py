from django.contrib import admin
from . models import Payment, Order, OrderProduct, OrderDelivery
# Register your models here.
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'ordered')
    extra = 0

class OrderDeliveryInline(admin.TabularInline):
    model = OrderDelivery
    readonly_fields = ('courier', 'cost', 'total_weight')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'address', 'order_total', 'tax', 'status', 'is_ordered', 'payment', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'is_orderet']
    list_per_page = 20
    inlines = [
        OrderProductInline,
        OrderDeliveryInline
    ]

@admin.register(Payment)
class PaymenAdmin(admin.ModelAdmin):
    list_display = ['payment_id', 'payment_method', 'amount_paid', 'payment_type', 'status', 'created_at']
    search_fields = ['user', 'payment_method']
    list_per_page = 20

admin.site.register(OrderProduct)
admin.site.register(OrderDelivery)