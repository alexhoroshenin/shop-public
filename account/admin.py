from django.contrib import admin
from .models import Profile

admin.site.register(Profile)


class ProfileAdmin(admin.ModelAdmin):
    pass
