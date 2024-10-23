from django.contrib import admin
from . models import Product, ProductItem, Variation, ReviewRating, ProductGallery, ProductPaket, ViewCount
import admin_thumbnails

# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProdutGalleryInline(admin.TabularInline):
    model = ProductGallery
    readonly_fields = ('id',)
    extra = 0

class ProductPaketInline(admin.TabularInline):
    model = ProductPaket
    extra = 0
    fieldsets = [
        (
            None,
            {
                "fields": ["weight"],
            },
        ),
        (
            "Advanced options",
            {
                "classes": ["collapse"],
                "fields": ["length", "width", "height"],
            },
        )
    ]
    classes = ('collapse', )
    
class ProdutItemInline(admin.TabularInline):
    model = ProductItem
    readonly_fields = ('id',)
    show_change_link = True
    extra = 0
    # classes = ('collapse', )

@admin.register(Product)
@admin_thumbnails.thumbnail('images')
class ProductAdmin(admin.ModelAdmin):
    '''Admin View for Product'''
    inlines = [
        ProdutGalleryInline,
        ProdutItemInline,
        ProductPaketInline,
        ]
    
    def get_inline_instances(self, request, obj=None):
        return [inline(self.model, self.admin_site) for inline in self.inlines]

    list_display = ('images_thumbnail', 'name', 'category', 'is_available')
    prepopulated_fields = {'slug': ('name',)}
    # 
    list_filter = ('name',)
    raw_id_fields = ('category',)
    # readonly_fields = ('',)
    search_fields = ('name',)
    date_hierarchy = 'created_date'
    # ordering = ('',)
    # 

class ProductVariantInline(admin.TabularInline):
    model = Variation
    extra = 0

@admin.register(ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    inlines = [
        ProductVariantInline,
    ]
    
    def get_inline_instances(self, request, obj=None):
        return [inline(self.model, self.admin_site) for inline in self.inlines]      

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product_item', 'varian_category', 'variation_value', 'is_active')
    list_editable = ('is_active',)
    list_filter = ('product_item', 'varian_category', 'variation_value')
admin.site.register(Variation, VariationAdmin)

admin.site.register(ReviewRating)
admin.site.register(ProductGallery)
admin.site.register(ProductPaket)
admin.site.register(ViewCount)