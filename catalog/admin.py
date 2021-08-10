from django.contrib import admin

from .models import Category, Product, ProductImage, StockBalance, Warehouse

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name', 'id_1c']

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_percent', 'date_created')
    # list_filter = ('price', )
    search_fields = ['name', 'id_1c']

class WarehouseAdmin(admin.ModelAdmin):
    pass

class ProductToWarehouseAdmin(admin.ModelAdmin):
    search_fields = ['product__name']

class ProductImageAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(StockBalance, ProductToWarehouseAdmin)
admin.site.register(Warehouse, WarehouseAdmin)
