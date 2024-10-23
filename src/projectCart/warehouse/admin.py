from django.contrib import admin
from . models import *

admin.site.register(Brand)
admin.site.register(Product)
admin.site.register(ProductAttribute)
admin.site.register(ProductAttributeValue)
admin.site.register(ProductAttributeValues)
admin.site.register(ProductType)

@admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):
    list_display = ('sku', 'upc',)
