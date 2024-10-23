from django.contrib import admin
from .  models import Category
import admin_thumbnails


@admin_thumbnails.thumbnail('cat_image')
class CatigoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name', )}
    list_display = ('category_name', 'parent', 'slug')
admin.site.register(Category, CatigoryAdmin)