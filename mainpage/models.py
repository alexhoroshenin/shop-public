from django.db import models
from sorl.thumbnail import ImageField
from .utils import get_banner_upload_path
from django.utils import timezone
from django.conf import settings


class Banner(models.Model):
    """Модель баннера на главной странице"""
    name = models.CharField(max_length=128, blank=False, null=False)
    image = ImageField(upload_to=get_banner_upload_path, max_length=255, null=True)
    url = models.CharField(max_length=256, blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    show = models.BooleanField(default=True)

    class Meta:
        app_label = 'mainpage'
        ordering = ["-date_created"]

    def __str__(self):
        return f"{self.name}"


class ClientMessage(models.Model):
    """Модель сообщения клиента из обратной связи"""
    name = models.CharField(max_length=250, blank=True, null=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    date_created = models.DateTimeField(default=timezone.now, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'mainpage'
        ordering = ["-date_created"]

    def __str__(self):
        return f"{self.name}"
