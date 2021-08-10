from django.conf import settings
# from catalog.forms import SearchForm


def append_default_product_image(request):
    return {
        'DEFAULT_PRODUCT_IMAGE': settings.DEFAULT_PRODUCT_IMAGE,
        'SHOP_TITLE': settings.SHOP_TITLE
    }
