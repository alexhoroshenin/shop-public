from django.contrib import admin
from .models import Cart, CartItem, DeliveryMethod, PaymentMethod

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(DeliveryMethod)
admin.site.register(PaymentMethod)

class CartAdmin(admin.ModelAdmin):
    pass

class CartItemAdmin(admin.ModelAdmin):
    pass
