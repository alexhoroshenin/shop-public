from django.contrib import admin
from .models import Order, Address, OrderItem


class OrderAdmin(admin.ModelAdmin):
    pass


class OrderItemAdmin(admin.ModelAdmin):
    pass


class AddressAdmin(admin.ModelAdmin):
    pass


admin.site.register(Order, OrderAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
