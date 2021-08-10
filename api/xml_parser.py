"""Модуль парсинга XML"""
from xml.etree import cElementTree as ET


class Product:
    """Объект - продукт, полученный парсером из файла"""
    def __init__(self, id_1c, name, description=None, groups=None):
        self.id_1c = id_1c
        self.name = name
        self.description = description
        self.groups = groups

    def __repr__(self):
        return self.name


class Group:
    """Объект - категория, полученный парсером из файла"""
    def __init__(self, id_1c, name, description=None, parent_id_1c=None):
        self.id_1c = id_1c
        self.name = name
        self.description = description
        self.parent_id_1c = parent_id_1c

    def __repr__(self):
        return self.name


class Stock:
    """Объект - склад, полученный парсером из файла"""
    def __init__(self, id_1c, name):
        self.id_1c = id_1c
        self.name = name

    def __repr__(self):
        return self.name


class Offer:
    """Объект - Предложение, полученный парсером из файла"""
    def __init__(self, product_id_1c, price=0, stocks=None):
        self.product_id_1c = product_id_1c
        self.price = price
        self.stocks = {} if not stocks else stocks

    def __repr__(self):
        return self.product_id_1c


class XMLParser:
    """Класс Парсер, обработчик XML - файла"""
    def __init__(self, xml_file=None, xml_string=None):
        self.xml_file = xml_file
        self.xml_string = xml_string
        self.group_list = list()
        self.product_list = list()
        self.stocks_list = list()
        self.offers_list = list()
        # self.ns = {'ns': 'urn:1C.ru:commerceml_2'}
        self.ns = None

    def get_ns(self, tree):
        """из строки '{urn:1C.ru:commerceml_210}КоммерческаяИнформация' извлекет 'urn:1C.ru:commerceml_210'
        и запишет в совойство класса"""

        root = tree.getroot()
        tag = root.tag
        ns = tag.split('{')[1].split('}')[0]
        self.ns = {'ns': ns}

    def parse_file(self):
        tree = ET.parse(self.xml_file)
        self.get_ns(tree)

        group_root = tree.findall('.//ns:Классификатор/ns:Группы/', self.ns)
        if not group_root:
            group_root = tree.findall('.//ns:Классификатор/ns:Категории/', self.ns)

        product_root = tree.findall('.//ns:Каталог/ns:Товары/', self.ns)
        stocks_root = tree.findall('.//ns:ПакетПредложений/ns:Склады/', self.ns)
        offers_root = tree.findall('.//ns:ПакетПредложений/ns:Предложения/', self.ns)
        if not stocks_root:
            stocks_root = tree.findall('.//ns:ИзмененияПакетаПредложений/ns:Склады/', self.ns)

        if not offers_root:
            offers_root = tree.findall('.//ns:ИзмененияПакетаПредложений/ns:Предложения/', self.ns)

        if offers_root and not stocks_root:
            # В этом случае дерево складов отсуствует в файле. Склады нужно брать из первого предложения
            self._create_stocks(offers_root[0].findall('ns:Склады', self.ns))

        if group_root:
            self._create_groups(group_root)
        if product_root:
            self._create_products(product_root)
        if stocks_root:
            self._create_stocks(stocks_root)
        if offers_root:
            self._create_offers(offers_root)

    def _get_groups_id_1c_for_product(self, etree_product):
        """Возвращает список групп из дерева товара"""
        # tree.findall('.//ns:Каталог/ns:Товары/', ns)[0].findall('./ns:Группы/', ns).text
        groups = set()
        etree_groups = etree_product.findall('./ns:Группы/', self.ns)
        if etree_groups:
            for g in etree_groups:
                groups.add(g.text)
        else:
            # Для другого формата XML
            groups.add(etree_product.find('ns:Категория', self.ns).text)

        return list(groups)

    def _create_products(self, product_root):
        """Парсинг продуктов"""
        for p in product_root:
            id_1c = p.find('ns:Ид', self.ns).text
            name = p.find('ns:Наименование', self.ns).text
            description = p.find('ns:Описание', self.ns).text
            groups = self._get_groups_id_1c_for_product(p)
            product = Product(id_1c, name, description, groups)
            self.product_list.append(product)

    def _create_groups(self, etree_groups, parent_id_1c=None):
        """Парсинг групп(категорий)"""
        for g in etree_groups:
            id_1c = g.find('ns:Ид', self.ns).text
            name = g.find('ns:Наименование', self.ns).text
            group = Group(id_1c, name, parent_id_1c=parent_id_1c)
            self.group_list.append(group)

            sub_groups = g.find('ns:Группы', self.ns)
            if sub_groups:
                self._create_groups(sub_groups, parent_id_1c=id_1c)

    def _create_stocks(self, stocks_root):
        """Парсинг складов"""
        for i, stock in enumerate(stocks_root, start=1):
            id_1c = stock.find('ns:Ид', self.ns)

            if id_1c != None:
                id_1c = id_1c.text
            else:
                id_1c = stock.attrib.get('ИдСклада')

            if not id_1c:
                break

            name = stock.find('ns:Наименование', self.ns)
            if name:
                name = name.text
            else:
                name = f'Склад №{i}'

            stock = Stock(id_1c, name)
            self.stocks_list.append(stock)

    def _create_offers(self, offers_root):
        """Парсинг Преложений с остатками
        Из 1с могут прийти дубли предложений, которые отличаются только характеристиками.
        То есть для одного продукта может быть несколько прделожений.
        Учет характеристик сейчас не ведется, поэтому для исключения дублей искользуем словарь,
        сохраняем записи {product_id_1c: Объект Offer}
        Таким образом для ключа product_id_1c  будет только один Оффер, последний, который был в XML

        Возвращает списк items from dict
        """
        new_offers = {}
        for o in offers_root:
            product_id_1c = o.find('ns:Ид', self.ns).text
            stocks = dict()

            price = 0
            try:
                price = float(o.find('ns:Цены', self.ns)[0].find('ns:ЦенаЗаЕдиницу', self.ns).text)
            except:
                pass

            current_stocks = o.findall('ns:Склад', self.ns)
            if not current_stocks:
                current_stocks = o.findall('ns:Склады', self.ns)

            for s in current_stocks:
                quantity = s.attrib.get('КоличествоНаСкладе')
                stock_id_1c = s.attrib.get('ИдСклада')

                try:
                    quantity = float(quantity)
                except:
                    quantity = 0

                if quantity < 0:
                    quantity = 0

                stocks.update({
                    stock_id_1c: quantity
                })

            offer = Offer(product_id_1c, price, stocks)
            new_offers[product_id_1c] = offer

        self.offers_list = list(new_offers.values())


def main():
    """Тестовые запуски в ручном режиме"""

    file1 = '/home/dev/PycharmProjects/django-shop/shop/xmlparser/offers0_1_BIG.xml'
    file2 = '/home/dev/PycharmProjects/django-shop/shop/xmlparser/offers0_1_BIG.xml'

    file3 = '/home/dev/PycharmProjects/django-shop/shop/offers0_1_BIG.xml'
    file4 = '/home/dev/PycharmProjects/django-shop/shop/offers0_1_BIG.xml'

    xml_parser = XMLParser(xml_file=file3)

    xml_parser.parse_file()
    print()


if __name__ == '__main__':
    main()