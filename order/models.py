from django.db import models
from django.conf import settings
from .utils import get_str_date


class Order(models.Model):
    """Модель заказа"""

    NEW, IN_PROCESS, DELIVERY, COMPLETE, CANCELED = (
        "Новый", "В обработке", "В доставке", "Завершен", "Отменен")

    STATUS_CHOICES = (
        (NEW, "Новый"),
        (IN_PROCESS, "В обработке"),
        (DELIVERY, "В доставке"),
        (COMPLETE, "Завершен"),
        (CANCELED, "Отменен"),
    )

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    additional_info = models.CharField(max_length=256, blank=True, null=True)
    date_created = models.DateTimeField(db_index=True, auto_now=True)

    status = models.CharField(max_length=128, default=NEW, choices=STATUS_CHOICES)
    cart = models.ForeignKey('cart.Cart', on_delete=models.DO_NOTHING, blank=False, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    payment_method = models.ForeignKey('cart.PaymentMethod', on_delete=models.DO_NOTHING, null=True, blank=True)
    delivery_method = models.ForeignKey('cart.DeliveryMethod', on_delete=models.DO_NOTHING, null=True, blank=True)
    shipping_address = models.ForeignKey('order.Address', blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        app_label = 'order'
        ordering = ['-date_created']

    @property
    def date_created_str(self):
        """Дата в формате 01.01.2021"""
        return get_str_date(self.date_created)

    def get_total(self):
        """Возвращает итоговую сумму заказа"""
        total = 0
        for item in self.order_items.all():
            total += item.get_total()
        return total

    def __str__(self):
        return f'Заказ {self.pk} от {self.date_created_str}, статус {self.status}'


class OrderItem(models.Model):
    """Модель единицы заказа"""
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    quantity = models.FloatField(default=1, blank=False, null=False)
    price = models.FloatField(default=0, blank=False, null=False)
    order = models.ForeignKey('order.Order', on_delete=models.CASCADE, related_name='order_items')

    class Meta:
        app_label = 'order'
        ordering = ['-order', 'product']

    def get_total(self):
        """Возвращает итоговую стоимость единицы заказа"""
        return self.price * self.quantity

    def __str__(self):
        return f"{self.order}, {self.product}, {self.quantity}, {self.price}"


class OrderItemToWarehose(models.Model):
    """Модель записи о списании товара со склада"""
    orderitem = models.ForeignKey('order.OrderItem', on_delete=models.CASCADE, blank=False, null=False)
    warehouse = models.ForeignKey('catalog.Warehouse', on_delete=models.CASCADE, blank=False, null=False)
    subtracted_quantity = models.FloatField(default=0, blank=False, null=False)

    class Meta:
        app_label = 'order'
        ordering = ['orderitem', 'subtracted_quantity']

    def __str__(self):
        return f"Заказ: {self.orderitem.order.pk}, " \
               f"Товар: {self.orderitem.product}, " \
               f"Склад: {self.warehouse}, " \
               f"Заказаное количество: {self.subtracted_quantity}"


class Address(models.Model):
    """Модель сохраненного адреса клиента"""
    postcode = models.CharField(max_length=64, blank=True, null=True)
    state = models.CharField(max_length=128, blank=True, null=True)
    country = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    address_line = models.CharField(max_length=256, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        app_label = 'order'
        ordering = ['city']

    def __str__(self):
        postcode = f'{self.postcode}' if self.postcode else ''
        country = f', {self.country}' if self.country else ''
        state = f', {self.state}' if self.state else ''
        city = f', {self.city}' if self.city else ''
        address_line = f', {self.address_line}' if self.address_line else ''

        return f'{postcode}{country}{state}{city}{address_line}'
