from pathlib import Path
import math
from django.conf import settings
from django.utils.text import slugify


def generate_slug(title):
    """Создает slug для строки"""
    converter = settings.SLUG_CONVERTER

    slug = ''
    for char in title.lower():
        translit_char = converter.get(char, char)
        slug += translit_char

    slug = slugify(slug)
    return slug


def get_image_upload_path(instance, filename):
    return str(Path(settings.IMAGE_FOLDER, filename))


def get_discount_value(price, discount_percent):
    """Возвращает значение скидки в единицах измерения цены.
    Например, товар стоит 100 руб, скидка 10%. Вернет 10 (руб)"""
    if price and discount_percent and (0 < discount_percent < 100):
        return math.floor(price * discount_percent / 100)
    return 0


def get_price_with_discount(price, discount_percent):
    """Возвращает цену с учетом скидки"""
    return price - get_discount_value(price, discount_percent)
