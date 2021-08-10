from django.contrib import admin
from .models import Banner, ClientMessage


class BannerAdmin(admin.ModelAdmin):
    pass


class ClientMessageAdmin(admin.ModelAdmin):
    list_display = ('date_created', 'name', 'user')


admin.site.register(Banner, BannerAdmin)
admin.site.register(ClientMessage, ClientMessageAdmin)
