from cart.utils import get_active_cart


class AppendCartIntoRequest:
    """Добавляет корзину в request"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        request.cart = get_active_cart(request)
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        return response
