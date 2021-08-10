from django.db import models
from django.db.models import Sum, F, Case, Value, When, BooleanField, Prefetch
from catalog.models import Product, ProductImage
from django.conf import settings
from django.utils import timezone

from django.db import connection


class Cart(models.Model):

    OPEN, SAVED, SUBMITTED, MERGED = (
        "Open", "Saved", "Submitted", "Merged")

    STATUS_CHOICES = (
        (OPEN, "Open - currently active"),
        (SAVED, "Saved - for items to be purchased later"),
        (SUBMITTED, "Submitted - has been ordered at the checkout"),
        (MERGED, "Merged - superceded by another basket"),
    )

    status = models.CharField(max_length=128, default=OPEN, choices=STATUS_CHOICES)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        related_name='carts',
        on_delete=models.SET_NULL)

    date_created = models.DateTimeField(auto_now_add=True)
    date_submitted = models.DateTimeField(null=True, blank=True)
    date_merged = models.DateTimeField(null=True, blank=True)

    payment_method = models.ForeignKey('cart.PaymentMethod', on_delete=models.DO_NOTHING, db_index=False,
                                       null=True, blank=True)
    delivery_method = models.ForeignKey('cart.DeliveryMethod', on_delete=models.DO_NOTHING, db_index=False,
                                        null=True, blank=True)

    class Meta:
        app_label = 'cart'

    def append_item(self, product, count=1):
        """Добавляет товар в корзину"""

        cart_items = self.cart_items.filter(product=product)
        if cart_items.count() == 0:
            CartItem.objects.create(cart=self, product=product, quantity=count)
        else:
            self.change_item_count(cart_items[0].pk, count)

    def change_item_count(self, item_pk, item_count):
        """Меняет количество товара в корзине"""

        item_count = float(item_count)
        if self.is_correct_count_input(item_count):
            item = self.cart_items.get(pk=item_pk)
            if item_count == 0:
                item.delete()
            else:
                item.quantity = item_count
                item.save()

            self.delete_zero_value_items()
        else:
            raise ValueError

    def is_correct_count_input(self, value):
        """Проверка корректности количества"""
        if value and isinstance(value, (int, float)) and value >= 0:
            return True
        return False

    def delete_item(self, item_pk):
        """Удаляет товар из корзины"""
        self.cart_items.filter(pk=item_pk).delete()
        self.delete_zero_value_items()

    def delete_zero_value_items(self):
        """Удаляет товары из корзины с нулевым количеством"""
        self.cart_items.filter(quantity__lte=0).delete()

    def merge_cart_with(self, cart_to_append):
        """Мержит корзины, например, при авторизации пользователя"""
        self.date_merged = timezone.now()

        for item_to_append in cart_to_append.items.all():

            for current_item in self.cart_items.all():
                if current_item.product == item_to_append.product:
                    current_item.quantity += item_to_append.quantity
                    current_item.save()
                    break
            else:
                new_item = CartItem(product=item_to_append.product,
                                    quantity=item_to_append.quantity,
                                    cart=self)
                new_item.save()

        self.save()
        cart_to_append.status = Cart.MERGED
        cart_to_append.save()

    def set_user(self, user):
        self.user = user
        self.save()

    def get_list_with_products(self):
        return [x.product for x in self.cart_items.all()]

    def get_dict_with_products_and_count(self):
        return {x.product: x.quantity for x in self.cart_items.all()}

    def get_count_of_product_by_product_obj(self, product):
        try:
            item = self.cart_items.get(product=product)
            return item.quantity
        except:
            return 0

    def get_count_of_product_by_item_pk(self, item_pk):
        try:
            item = self.cart_items.get(pk=item_pk)
            return item.quantity
        except:
            return 0

    def get_cart_item_by_product_pk(self, product_pk):
        cart_items = self.cart_items.filter(product__pk=product_pk)
        if cart_items:
            return cart_items[0]
        return None

    def get_cart_items_with_balance(self):
        """Возврыщает queryset cart_items с балансом на складе"""
        products_with_balance = self.cart_items \
            .select_related('product') \
            .annotate(balance=Sum('product__stockbalance__balance')) \
            .annotate(exceed_balance=Case(When(balance__gte=F('quantity'), then=Value(False)), default=Value(True),
                                          output_field=BooleanField()))

        return products_with_balance

    def is_exceed_balance(self):
        """Проверка на превышение баланса товаров на складе"""

        cart_items_with_balance = self.get_cart_items_with_balance()
        products_with_excess_balance = cart_items_with_balance.filter(exceed_balance=True)

        return products_with_excess_balance.count()

    def get_cart_items_for_render(self):

        items_for_render = self.cart_items \
            .select_related('product') \
            .prefetch_related('product__images') \
            .annotate(balance=Sum('product__stockbalance__balance')) \
            .annotate(exceed_balance=Case(When(balance__gte=F('quantity'), then=Value(False)), default=Value(True),
                                          output_field=BooleanField()))

        return items_for_render

    def get_result(self):
        """Возвращает итоги корзины"""
        products_cost = 0
        discount_sum = 0
        for item in self.cart_items.all():
            if item.product.has_discount():
                discount_price = item.product.get_discount_price()
                products_cost += discount_price * item.quantity
                discount_sum += (item.product.price - discount_price) * item.quantity
            else:
                products_cost += item.product.price * item.quantity

        if self.delivery_method:
            delivery_cost = self.delivery_method.price
        else:
            delivery_cost = 0

        total = products_cost + delivery_cost - discount_sum

        return {'products_cost': products_cost,
                'delivery_cost': delivery_cost,
                'discount_sum': discount_sum,
                'total_count': self.cart_items.count(),
                'total': total}


class CartItem(models.Model):
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    quantity = models.FloatField(default=1)
    cart = models.ForeignKey('cart.Cart', on_delete=models.CASCADE, related_name='cart_items', db_index=True)

    @property
    def total_cost_with_discount(self):
        return self.quantity * self.product.get_discount_price()

    @property
    def total_cost_without_discount(self):
        return self.quantity * self.product.price

    class Meta:
        app_label = 'cart'
        ordering = ['cart', 'product']


class DeliveryMethod(models.Model):
    name = models.CharField(max_length=64, blank=True)
    price = models.FloatField(blank=True, default=0)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = 'cart'
        ordering = ['price']

    def __str__(self):
        decs = f', {self.description}' if self.description else ''
        price = f', {self.price} руб' if self.price else ''

        return f'{self.name}{price}{decs}'


class PaymentMethod(models.Model):
    name = models.CharField(max_length=64, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = 'cart'
        ordering = ['name']

    def __str__(self):
        decs = f', {self.description}' if self.description else ''
        return f'{self.name}{decs}'
