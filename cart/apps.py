from django.apps import AppConfig


class CartConfig(AppConfig):
    name = 'cart'

    def ready(self):
        """Подключение сигналов"""
        from . import signals
