from .models import Cart
from account.utils import get_user_from_request


def get_cart_or_create_new(request):
    cart = get_active_cart(request)
    if not cart:
        cart = create_cart(request)
    return cart


def create_cart(request):
    user = get_user_from_request(request)
    cart = Cart.objects.create(user=user, status='OPEN')

    if not user:
        append_cart_pk_to_session(request, cart.pk)

    return cart


def append_cart_pk_to_session(request, cart_pk):
    request.session['cart_pk'] = cart_pk


def get_active_cart(request):
    """Возвращает активную корзину для пользователя"""

    if hasattr(request, 'cart'):
        # Если корзина уже получена в middleware, то вернет ее
        return request.cart

    user = get_user_from_request(request)

    if user:
        # ищем корзину для аваторизованного пользователя
        try:
            cart = Cart.objects.get(user=user, status='OPEN')
        except:
            cart = None
    else:
        # ищем корзину по cart_pk из сессии
        cart_pk = request.session.get('cart_pk')
        try:
            cart = Cart.objects.get(pk=cart_pk, status='OPEN')
        except:
            cart = None

    return cart


def create_choises_for_form(queryselect):
    """Формирует кортежи для choises"""
    choises = []
    for obj in queryselect:
        choises.append(tuple([obj.pk, obj.name]))

    return choises
