from django.contrib import admin
from accounts import models

from store.models import Product, ProductGallary, ReviewRating, Variation
import admin_thumbnails

# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallary
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','price','stock','category','modified_date','is_available')
    prepopulated_fields = {"slug": ("product_name",)}
    inlines = [ProductGalleryInline]
admin.site.register(Product,ProductAdmin)


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category','variation_value','is_active','created_date')
    list_editable =('is_active',)
    list_filter = ('product','variation_category','variation_value')
admin.site.register(Variation,VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallary)