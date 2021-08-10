"""Модуль загрузки распарсенных данных в базу магазина"""
import json
from itertools import islice
from pathlib import Path
from django.conf import settings
from django.db.models import F, Value
from django.db.models.functions import Concat
from catalog.models import Product, Category, StockBalance, Warehouse, ProductImage, generate_slug
from catalog.utils import get_image_upload_path


class JsonLoader:
    """Загружает данные в базу
    """
    def __init__(self, input_json_converter):
        self.input_json_converter = input_json_converter
        self._load()

    def _load(self):

        if self.input_json_converter.category:
            CategoryLoader(Category, self.input_json_converter.category)

        if self.input_json_converter.product:
            ProductLoader(Product, self.input_json_converter.product)


class XmlLoader:
    """Загружает данные из XML в базу"""
    def __init__(self, input_xml_parser):
        self.input_xml_parser = input_xml_parser
        self._load()

    def _load(self):

        if self.input_xml_parser.group_list:
            CategoryLoader(data=self.input_xml_parser.group_list)

        if self.input_xml_parser.product_list:
            ProductLoader(data=self.input_xml_parser.product_list)

        if self.input_xml_parser.stocks_list:
            StockLoader(data=self.input_xml_parser.stocks_list)

        if self.input_xml_parser.offers_list:
            OfferLoader(data=self.input_xml_parser.offers_list)


class AbstractModelLoader:
    """Абстрактный класс загрузки данных в базу джанго"""
    def __init__(self, model, data, *args, **kwargs):
        self.model = model
        self.input_data = data
        self.items_from_db = None
        self.load()

    def load(self):
        if not self.input_data:
            return
        self._get_exist_data_from_db()
        self._compare_data()
        self._save_updated_data()

    def _get_exist_data_from_db(self):
        pass

    def _compare_data(self):
        for input_obj in self.input_data:
            obj_from_db = self.items_from_db.get(input_obj.id_1c)
            if obj_from_db:
                self._update_object_if_different(obj_from_db, input_obj)
            else:
                self._create_object(input_obj)

    def _create_object(self, obj_from_parser):
        pass

    def _update_object_if_different(self, obj_from_db, obj_from_parser):
        pass

    def _save_updated_data(self):
        pass


class ProductLoader(AbstractModelLoader):
    """Обновляет сущесвтующие товары и сохраняет новые в базу"""
    def __init__(self, data, *args, **kwargs):
        self.category_from_db = None
        self.products_to_creating = []
        super().__init__(Product, data, *args, **kwargs)

    def _get_exist_data_from_db(self):
        """Получение существующих данных из базы"""
        self.products_from_db = self.model.objects.filter(id_1c__isnull=False) \
            .select_related('main_category') \
            .annotate(main_category_id_1c=F('main_category__id_1c')) \
            .in_bulk(field_name='id_1c')

        # self.category_from_db = {x.id_1c: x for x in Category.objects.all()}
        self.category_from_db = Category.objects.filter(id_1c__isnull=False).in_bulk(field_name='id_1c')

    def _compare_data(self):
        for obj_from_parser in self.input_data:
            obj_from_db = self.products_from_db.get(obj_from_parser.id_1c)
            if obj_from_db:
                self._update_object_if_different(obj_from_db, obj_from_parser)
            else:
                self._create_object(obj_from_parser)

    def _create_object(self, obj_from_parser):

        main_category = self._get_main_category(obj_from_parser)

        self.products_to_creating.append(
            self.model(name=obj_from_parser.name,
                       description=obj_from_parser.description,
                       id_1c=obj_from_parser.id_1c,
                       slug=generate_slug(obj_from_parser.name),
                       main_category=main_category)
        )

    def _get_main_category(self, obj):
        """Возвращает объект основной категории товара, если он есть, иначе None"""
        if hasattr(obj, 'category_id_1c'):
            # Для входных данных из JSON
            return self.category_from_db.get(obj.category_id_1c)

        if hasattr(obj, 'groups') and len(obj.groups) > 0:
            # Для входных данных из XML, когда указано несколько категорий товара. Первая становится основной.
            return self.category_from_db.get(obj.groups[0])

        return None

    def _update_object_if_different(self, obj_from_db, obj_from_parser):
        """Обновляет товар, если были изменения. Если изменений не было, удаляет товар из списка bulk update"""
        changes = False
        if obj_from_db.name != obj_from_parser.name or obj_from_db.description != obj_from_parser.description:
            changes = True
            obj_from_db.name = obj_from_parser.name
            obj_from_db.description = obj_from_parser.description

        if hasattr(obj_from_parser, 'category_id_1c') and \
                obj_from_db.main_category_id_1c != obj_from_parser.category_id_1c:
            changes = True
            obj_from_db.main_category = self._get_main_category(obj_from_parser)

        if hasattr(obj_from_parser, 'groups') and \
                len(obj_from_parser.groups) > 0 and \
                obj_from_db.main_category_id_1c != obj_from_parser.groups[0]:
            changes = True
            obj_from_db.main_category = self._get_main_category(obj_from_parser)

        if not changes:
            self.products_from_db.pop(obj_from_db.id_1c, None)

    def _save_updated_data(self):
        """Сохраняет и обновляет объекты через массовове обновление.
        batch_size = 1000 - оптимальное значение
        Если выбрать больше, есть вероятность зависания базы
        """

        batch_size = 1000
        self.model.objects.bulk_update(self.products_from_db.values(),
                                       ['name', 'description', 'main_category'],
                                       batch_size=batch_size)

        for start in range(0, len(self.products_to_creating), batch_size):
            self.model.objects.bulk_create(
                list(islice(self.products_to_creating, start, start + batch_size)),
                batch_size=batch_size
           )


class CategoryLoader(AbstractModelLoader):
    """Загрузчик категорий в базу"""
    def __init__(self, *args, **kwargs):
        super().__init__(model=Category, *args, **kwargs)

    def _get_exist_data_from_db(self):
        self.data_from_db = self.model.objects.filter(id_1c__isnull=False)\
            .in_bulk(field_name='id_1c')

    def _compare_data(self):
        """Сначала создадим новые категории.
        Чтобы затем можно было присвоить родителей для категорий. А для этого уже должен быть объект родительской
        категории в базе"""
        for input_obj in self.input_data:
            obj_from_db = self.data_from_db.get(input_obj.id_1c)
            if not obj_from_db:
                self._create_object(input_obj)

        # Обновим данные из базы
        self._get_exist_data_from_db()

        for input_obj in self.input_data:
            obj_from_db = self.data_from_db.get(input_obj.id_1c)
            self._update_object_if_different(obj_from_db, input_obj)

    def _create_object(self, obj):
        """Созлание новых категорий
        К операции не применимо BULK create, потому модель категории создана с наследованием
        """
        parent = self._get_parent(obj)
        self.model.objects.create(name=obj.name,
                                  description=obj.description,
                                  id_1c=obj.id_1c,
                                  parent=parent)

    def _get_parent(self, obj):
        """Возвращает объект родительской категории"""
        if not hasattr(obj, 'parent_id_1c') or not obj.parent_id_1c:
            return None

        parent = self.data_from_db.get(obj.parent_id_1c)
        return parent

    def _update_object_if_different(self, obj_from_db, obj_from_parser):

        changes = False
        if obj_from_db.name != obj_from_parser.name:
            obj_from_db.name = obj_from_parser.name
            changes = True

        if hasattr(obj_from_parser, 'description') and obj_from_db.description != obj_from_parser.description:
            obj_from_db.description = obj_from_parser.description
            changes = True

        input_parent_id_1c = getattr(obj_from_parser, 'parent_id_1c', None)
        if input_parent_id_1c and input_parent_id_1c != obj_from_db.parent:
            changes = True
            self._set_parent(obj_from_db, input_parent_id_1c)

        if not changes:
            self.data_from_db.pop(obj_from_db.id_1c, None)

    def _set_parent(self, obj_from_db, new_parent_id_1c):
        try:
            obj_from_db.parent = self.model.objects.get(id_1c=new_parent_id_1c)
        except self.model.DoesNotExist:
            obj_from_db.parent = None

    def _save_updated_data(self):
        self.model.objects.bulk_update(self.data_from_db.values(),
                                       ['name', 'description', 'parent'],
                                       batch_size=100)


class StockLoader(AbstractModelLoader):

    def __init__(self, data, *args, **kwargs):
        super().__init__(Warehouse, data, *args, **kwargs)

    def _get_exist_data_from_db(self):
        self.items_from_db = self.model.objects.filter(id_1c__isnull=False).in_bulk(field_name='id_1c')

    def _create_object(self, obj_from_parser):
        description = getattr(obj_from_parser, 'description', None)

        self.model.objects.create(name=obj_from_parser.name,
                                  id_1c=obj_from_parser.id_1c,
                                  description=description)

    def _update_object_if_different(self, obj_from_db, obj_from_parser):
        changes = False
        if obj_from_db.name != obj_from_parser.name:
            obj_from_db.name = obj_from_parser.name
            changes = True

        if hasattr(obj_from_parser, 'description') and obj_from_parser.description != obj_from_db.description:
            obj_from_db.description = obj_from_parser.description
            changes = True

        if not changes:
            self.items_from_db.pop(obj_from_db.id_1c, None)

    def _save_updated_data(self):
        self.model.objects.bulk_update(self.items_from_db.values(),
                                       ['name', 'description'])


class OfferLoader(AbstractModelLoader):
    """Загрузчик остатков и цен товаров"""
    def __init__(self, data, *args, **kwargs):
        self.balance_to_create_in_bulk = []
        self.products_from_db = None
        self.products_from_db_for_price_updating = []
        self.warehouses_from_db = None
        super().__init__(StockBalance, data, *args, **kwargs)

    def _get_exist_data_from_db(self):
        """
        Получаем из базы
        1. Существующие остатки на складах, чтобы обновить количество и создать новые записи
            Остатки формируем в хэш-таблицу с ключем product_id_1c ___ warehouse_id_1c
            По этому ключю будем осуществлять поиск для сравнения с данными парсера

        2. Список товаров, чтобы обновить цены
        3. Список складов, необходимых для создания новых записей Остатков
        """

        data_from_db = self.model.objects\
            .filter(product__id_1c__isnull=False, warehouse__id_1c__isnull=False)\
            .annotate(search_field=Concat(F('product__id_1c'), Value('___'),  F('warehouse__id_1c')))

        self.items_from_db = {x.search_field: x for x in data_from_db}
        self.items_from_db_in_bulk = \
            self.model.objects.filter(product__id_1c__isnull=False, warehouse__id_1c__isnull=False).in_bulk()

        self.products_from_db = Product.objects.filter(id_1c__isnull=False).in_bulk(field_name='id_1c')

        self.warehouses_from_db = Warehouse.objects.filter(id_1c__isnull=False).in_bulk(field_name='id_1c')

    def _compare_data(self):

        for obj_from_parser in self.input_data:
            product_id_1c = obj_from_parser.product_id_1c

            # У объекта из парсера есть dict {'склад_1':остаток, 'склад_1':остаток} для каждого товара
            for stock_id_1c, quantity in obj_from_parser.stocks.items():

                search_field = product_id_1c + "___" + stock_id_1c
                stock_balance_from_db = self.items_from_db.get(search_field)

                if not stock_balance_from_db and quantity > 0:
                    self._create_object(product_id_1c, stock_id_1c, quantity)

                if not stock_balance_from_db:
                    continue

                if stock_balance_from_db.balance != quantity:
                    self._update_object_if_different(stock_balance_from_db, quantity)
                else:
                    self.items_from_db_in_bulk.pop(stock_balance_from_db.pk, None)

            self._update_product_price(product_id_1c, obj_from_parser.price)

    def _create_object(self, product_id_1c, stock_id_1c, balance):
        product = self.products_from_db.get(product_id_1c)
        warehouse = self.warehouses_from_db.get(stock_id_1c)
        if product and warehouse:
            self.balance_to_create_in_bulk.append(
                self.model(product=product, warehouse=warehouse, balance=balance)
            )

    def _update_object_if_different(self, stock_balance_from_db, stock_balance_from_parser):
        balance_from_db = self.items_from_db_in_bulk.get(stock_balance_from_db.pk)
        if balance_from_db:
            balance_from_db.balance = stock_balance_from_parser

    def _update_product_price(self, product_id_1c, price_from_parser):
        product_from_db = self.products_from_db.get(product_id_1c)
        price_from_parser = float(price_from_parser)

        if product_from_db and product_from_db.price != price_from_parser:
            product_from_db.price = price_from_parser
            self.products_from_db_for_price_updating.append(product_from_db)

    def _save_updated_data(self):
        batch_size = 1000
        self.model.objects.bulk_update(self.items_from_db_in_bulk.values(),
                                       ['balance'], batch_size=batch_size)

        for start in range(0, len(self.balance_to_create_in_bulk), batch_size):
            self.model.objects.bulk_create(
                list(islice(self.balance_to_create_in_bulk, start, start + batch_size)),
                batch_size=batch_size
           )

        Product.objects.bulk_update(self.products_from_db_for_price_updating,
                                       ['price'], batch_size=batch_size)


class ImageLoader:

    def __init__(self, request, input_filepath):
        self.request = request
        self.input_filepath = input_filepath
        self.product_id_1c = None
        self.image_id_1c = None
        self.product = None
        self.exceptions = []
        self.filename = None
        self.absolute_path = None
        self.relative_path = None
        self.image_upload_path = None
        self.is_image_save = False

    def save_image(self):
        """Сохранение картинки"""
        self.filename = self.input_filepath.name
        self._get_product_id_and_image_id_from_filename(self.filename)

        if not self.product_id_1c or not self.image_id_1c:
            self.exceptions.append(f'Некорректное имя файла: {self.filename}')
            return

        self.absolute_path = self._get_absolute_path()
        self.relative_path = self._get_relative_path()
        self.exceptions = []

        self._get_product_by_id_1c()
        if not self.product:
            self.exceptions.append(f'Product with id {self.product_id_1c} not found')
            return

        self._save_file_if_not_exists()
        self._save_image_obj_into_db()

    def _get_absolute_path(self):
        return Path(settings.IMAGE_ROOT, self.filename)

    def _get_relative_path(self):
        return get_image_upload_path(instance=None, filename=self.filename)

    def _get_product_by_id_1c(self):
        try:
            self.product = Product.objects.get(id_1c=self.product_id_1c)
        except Exception:
            self.exceptions.append(f'Product with 1c_id: {self.product_id_1c} not found.')

    def file_exists(self):
        return self.absolute_path.is_file()

    def _save_file_if_not_exists(self):
        if not self.file_exists():
            try:
                self.absolute_path.write_bytes(self.request.body)
                self.is_image_save = True
            except Exception as e:
                self.exceptions.append(f'Error saving image for product {self.product_id_1c}')
                print(e)

    def _save_image_obj_into_db(self):
        product_images = list(self.product.images.filter(id_1c__isnull=False).values_list('display_order', 'image'))
        images_path = [im[1] for im in product_images]
        if self.relative_path not in images_path:
            try:
                max_display_order = max(x[0] for x in product_images) if product_images else 0
                current_display_order = max_display_order + 1
                ProductImage.objects.create(product=self.product,
                                            image=self.relative_path,
                                            display_order=current_display_order,
                                            id_1c=self.image_id_1c)

            except Exception:
                self.exceptions.append(f'An error occurred while saving an image.')


    def _get_product_id_and_image_id_from_filename(self, filename):
        """Из строки с именем картинки product_id_1c и image_id_1с товара
        48d21364ad3411e5acd4000d884fd00d-48d21364ad3411e5acd4000d884fd00d.jpg
        return product_id_1c = '48d21364-ad34-11e5-acd4-000d884fd00d'
        image_id_1с = '48d21364ad3411e5acd4000d884fd00d'
        """

        if "_" not in filename or len(filename) < 65:
            return

        raw_prod_id = filename.split('_')[0]
        image_name = filename.split('_')[1]
        image_id = Path(image_name).stem

        parts = list(raw_prod_id)
        first_insert = 8
        parts.insert(first_insert, '-')
        parts.insert(first_insert + 5, '-')
        parts.insert(first_insert + 5 + 5, '-')
        parts.insert(first_insert + 5 + 5 + 5, '-')

        prod_id = ''.join(parts)

        self.product_id_1c = prod_id
        self.image_id_1c = image_id

    @property
    def exceptions_as_json(self):
        exceptions = dict(errors=self.exceptions)
        exceptions_as_json = json.dumps(exceptions)
        return exceptions_as_json
