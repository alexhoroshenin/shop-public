from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from sorl.thumbnail import ImageField
from .utils import generate_slug, get_image_upload_path
from django.db.models import Sum
from django.utils import timezone
from .utils import get_discount_value, get_price_with_discount


class Warehouse(models.Model):
    """Модель склада"""
    name = models.CharField(max_length=128, db_index=True, blank=False)
    description = models.TextField(blank=True, null=True)
    id_1c = models.CharField(max_length=100, null=True, blank=True, unique=True)

    def __str__(self):
        return self.name


class StockBalance(models.Model):
    """Модель остатков на складе"""
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        db_index=True
    )

    warehouse = models.ForeignKey(
        'catalog.Warehouse',
        on_delete=models.CASCADE,
    )

    balance = models.FloatField(blank=True, default=0)

    class Meta:
        app_label = 'catalog'
        ordering = ['product', 'warehouse']
        unique_together = ('product', 'warehouse')

    def __str__(self):
        return f"{self.product}, склад: {self.warehouse}. остаток: {self.balance}"


class Category(MPTTModel):
    """Модель категории"""

    name = models.CharField(max_length=255, db_index=True, blank=False)
    description = models.TextField(blank=True, null=True)
    # image = models.ImageField(upload_to='categories', blank=True,
    #                           null=True, max_length=255)
    slug = models.SlugField(max_length=255, db_index=True, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    id_1c = models.CharField(max_length=100, null=True, blank=True, unique=True)

    class MPTTMeta:
        app_label = 'catalog'
        order_insertion_by = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name)

        super(Category, self).save(*args, **kwargs)

    def get_url(self):
        return f"{self.slug}-{self.pk}"

    def get_full_url(self):
        return f"catalog/{self.slug}-{self.pk}"


class Product(models.Model):
    """Модель товара"""
    name = models.CharField(max_length=128, db_index=True, blank=False)
    slug = models.SlugField(max_length=128, blank=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    model = models.CharField(max_length=128, blank=True, null=True, db_index=False)
    price = models.FloatField(blank=True, default=0)
    discount_percent = models.SmallIntegerField(blank=True, default=0, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    discount_finish_date = models.DateTimeField(blank=True, null=True)
    main_category = models.ForeignKey('catalog.Category', blank=True, null=True, on_delete=models.SET_NULL,
                                      related_name='products')

    optional_category = models.ManyToManyField('catalog.Category', blank=True)
    stock_balance_info = models.ManyToManyField('catalog.Warehouse',
                                                through='StockBalance',
                                                related_name='products')

    id_1c = models.CharField(max_length=100, null=True, blank=True, unique=True)

    class Meta:
        app_label = 'catalog'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.name)

        super(Product, self).save(*args, **kwargs)

    def get_full_url(self):
        return f"product/{self.slug}-{self.pk}"

    def get_primary_image(self):
        """Возвращает первую картинку"""
        return self.images.first()

    def get_discount_price(self):
        """Возвращает цену со скидкой"""
        return get_price_with_discount(self.price, self.discount_percent)

    def get_discount_value(self):
        """Возвращает значение скидки в единицах цены"""
        return get_discount_value(self.price, self.discount_percent)

    def get_balance(self):
        """Возвращает баланс товара"""
        return self.stock_balance_info.aggregate(Sum('stockbalance__balance'))['stockbalance__balance__sum']

    def get_warehouses_with_balance(self):
        """Возвращает список на записи с балансом товара"""
        return self.stock_balance_info.all()

    def has_discount(self):
        """Возвращает признак наличия скидки"""
        if self.discount_percent:
            return (self.discount_finish_date is None) or (self.discount_finish_date > timezone.now())
        return False

    @classmethod
    def get_balance_for_many_products(cls, list_of_products):
        """Обогащает сисок товаров значением баланса на складе"""
        if isinstance(list_of_products[0], int):
            return cls.objects.filter(pk__in=list_of_products).annotate(balance=Sum('stockbalance__balance'))
        elif isinstance(list_of_products[0], cls):
            return cls.objects.filter(pk__in=[i.pk for i in list_of_products]).annotate(balance=Sum('stockbalance__balance'))


class ProductImage(models.Model):
    """
    An image of a product
    """
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.CASCADE,
        db_index=True, related_name='images')

    image = ImageField(upload_to=get_image_upload_path, max_length=255)

    #: Use display_order to determine which is the "primary" image
    display_order = models.PositiveIntegerField(default=0, db_index=True,
                                                help_text=("An image with a display order of zero will be the primary"
                                                           " image for a product"))

    date_created = models.DateTimeField(auto_now_add=True)

    id_1c = models.CharField(max_length=100, null=True, blank=True, unique=True)

    class Meta:
        app_label = 'catalog'
        ordering = ["display_order", "-date_created"]

    def __str__(self):
        return f"Image of {self.product.name}, display_order: {self.display_order}, date_created: {self.date_created}"

    def is_primary(self):
        """
        Return bool if image display order is 0
        """
        return bool(self.display_order == 0)

    def delete(self, *args, **kwargs):
        """
        Always keep the display_order as consecutive integers
        """
        super().delete(*args, **kwargs)
        for id, image in enumerate(self.product.images.all()):
            image.display_order = id
            image.save()
