from django.apps import apps
from cart import utils as cart_utils


def append_cart(request):
    cart = cart_utils.get_active_cart(request)

    cart_products_list = cart.get_list_with_products() if cart else []
    cart_products_dict = cart.get_dict_with_products_and_count() if cart else {}

    return {
        'cart': cart,
        'cart_products_list': cart_products_list,
        'cart_products_dict': cart_products_dict
    }


def append_menu_items(request):

    model_categories = apps.get_model('catalog', 'Category')
    menu_main_categories = model_categories.objects.filter(parent=None)

    return {
        'menu_main_categories': menu_main_categories,
    }
