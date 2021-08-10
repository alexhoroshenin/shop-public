from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart


@receiver(user_logged_in)
def merge_carts(sender, **kwargs):
    """Объединят корзины пользователя в одну после успешной авторизации
    Если у неавторизованного пользователя есть открытая корзина в сессии, то он объединит ее с открытой корзиной
    авторизованного пользователя.
    Если у авторизованного нет открытх корзин, то добавить пользователя в корзину
    """
    request = kwargs.get('request')
    user = kwargs.get('user')

    if not request or not user or not user.is_authenticated:
        return None

    session_cart_pk = request.session.get('cart_pk')
    try:
        session_cart = Cart.objects.get(pk=session_cart_pk, status='OPEN')
    except:
        session_cart = None

    try:
        user_cart = Cart.objects.get(user=user, status='OPEN')
    except:
        user_cart = None

    if session_cart and not user_cart:
        session_cart.set_user(user)
        request.session.pop('cart_pk', default=None)

    if session_cart and user_cart:
        user_cart.merge_cart_with(session_cart)
        request.session.pop('cart_pk', default=None)

    print("Request finished!")
