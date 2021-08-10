import json
from django.shortcuts import render, HttpResponseRedirect, reverse, redirect
from django.http import JsonResponse
from django.views import View
from catalog.models import Product
from cart.models import Cart, CartItem, DeliveryMethod, PaymentMethod
from cart.utils import get_cart_or_create_new, get_active_cart, create_choises_for_form
from cart.forms import ProcessCartForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


class CartIndex(View):

    def get(self, request):
        delivery_methods = self._get_delivery_methods()
        payment_methods = self._get_payment_methods()
        form = ProcessCartForm()
        form.fields['delivery_method'].choices = create_choises_for_form(delivery_methods)
        form.fields['payment_method'].choices = create_choises_for_form(payment_methods)

        context = {'delivery_methods': delivery_methods,
                   'payment_methods': payment_methods,
                   'form': form,
                   'title': 'Корзина'}

        return render(request, 'cart.html', context)

    def post(self, request):
        delivery_methods = self._get_delivery_methods()
        payment_methods = self._get_payment_methods()
        form = ProcessCartForm(request.POST)
        form.fields['delivery_method'].choices = create_choises_for_form(delivery_methods)
        form.fields['payment_method'].choices = create_choises_for_form(payment_methods)

        if form.is_valid():
            cart = get_active_cart(request)
            payment_method_field_value = form.cleaned_data['payment_method']
            delivery_method_field_value = form.cleaned_data['delivery_method']
            if payment_method_field_value:
                payment_method = payment_methods.get(pk=int(payment_method_field_value))
                cart.payment_method = payment_method
                cart.save()
            if delivery_method_field_value:
                delivery_method = delivery_methods.get(pk=int(delivery_method_field_value))
                cart.delivery_method = delivery_method
                cart.save()

            if cart.is_exceed_balance():
                return redirect(reverse('cart:index'))

            return redirect(reverse('order:create_order'))
        else:
            context = {'delivery_methods': delivery_methods,
                       'payment_methods': payment_methods,
                       'form': form,
                       'title': 'Корзина'}

            return render(request, 'cart.html', context)


    def _get_delivery_methods(self):
        return DeliveryMethod.objects.all()

    def _get_payment_methods(self):
        return PaymentMethod.objects.all()


@method_decorator(csrf_exempt, name='dispatch')
class UpdateAjax(View):

    def post(self, request):

        body = json.loads(request.body)

        self.resp = {}
        self._change_delivery_method(request, body)
        self._change_payment_method(request, body)
        self._delete_cart_item_id(request, body)
        self._delete_product_from_cart_by_product_id(request, body)
        self._set_new_cart_item_count(request, body)
        self._append_product(request, body)
        self._change_product_count(request, body)

        if self.resp:
            return JsonResponse(self.resp)
        return JsonResponse(request.cart.get_result())


    def _change_delivery_method(self, request, body):
        delivery_method_id = body.get('delivery_method_id')

        if delivery_method_id:
            try:
                delivery_method_obj = DeliveryMethod.objects.get(pk=int(delivery_method_id))
                request.cart.delivery_method = delivery_method_obj
                request.cart.save()
            except:
                self.resp = {'error': 'Метод доставки с таким id не найден'}

    def _change_payment_method(self, request, body):
        payment_method_id = body.get('payment_method_id')
        if payment_method_id:
            try:
                payment_method_obj = PaymentMethod.objects.get(pk=int(payment_method_id))
                request.cart.payment_method = payment_method_obj
                request.cart.save()
            except:
                self.resp = {'error': 'Метод оплаты с таким id не найден'}

    def _delete_cart_item_id(self, request, body):
        delete_cart_item_id = body.get('delete_cart_item_id')
        if delete_cart_item_id:
            try:
                request.cart.delete_item(int(delete_cart_item_id))
            except:
                self.resp = {'error': 'Произошла ошибка при удалении товара из корзины'}

    def _delete_product_from_cart_by_product_id(self, request, body):
        delete_product_from_cart_by_product_id = body.get('delete_product_from_cart_by_product_id')
        if delete_product_from_cart_by_product_id:
            try:
                cart_item_obj = request.cart.get_cart_item_by_product_pk(delete_product_from_cart_by_product_id)
                request.cart.delete_item(cart_item_obj.pk)
            except:
                self.resp = {'error': 'Произошла ошибка при удалении товара из корзины'}

    def _set_new_cart_item_count(self, request, body):
        new_cart_item_count = body.get('new_cart_item_count')
        if new_cart_item_count:
            item_id = new_cart_item_count.get('item_id')
            new_item_count = float(new_cart_item_count.get('item_count'))

            try:
                cart_item_obj = request.cart.cart_items.get(pk=item_id)
                product_balance_float = cart_item_obj.product.get_balance()
                product_balance_int = int(product_balance_float)
                # Убираем нулевую десятичную часть
                if product_balance_float > product_balance_int:
                    product_balance = product_balance_float
                else:
                    product_balance = product_balance_int

                if product_balance < new_item_count:
                    response = {'value_error': f'Доступно: {product_balance}', 'available_count': product_balance}
                    request.cart.change_item_count(item_id, product_balance)

                    response.update(request.cart.get_result())
                    self.resp = response
                else:
                    request.cart.change_item_count(item_id, new_item_count)

            except:
                self.resp = {'error': 'Произошла ошибка при изменении количества'}

    def _append_product(self, request, body):
        append_product_id = body.get('append_product_id')
        if append_product_id:
            try:
                product = Product.objects.get(pk=int(append_product_id))
                request.cart.append_item(product)
            except:
                self.resp = {'error': 'Произошла ошибка при добавлении товара'}

    def _change_product_count(self, request, body):
        new_product_count = body.get('new_product_count')
        if new_product_count:
            product_id = new_product_count.get('product_id')
            new_product_count = float(new_product_count.get('product_count'))
            try:
                cart_item_obj = request.cart.get_cart_item_by_product_pk(product_id)
                product_balance_float = cart_item_obj.product.get_balance()
                product_balance_int = int(product_balance_float)
                # Убираем нулевую десятичную часть
                if product_balance_float > product_balance_int:
                    product_balance = product_balance_float
                else:
                    product_balance = product_balance_int

                if product_balance < new_product_count:
                    response = {'value_error': f'Доступно: {product_balance}', 'available_count': product_balance}
                    request.cart.change_item_count(cart_item_obj.pk, product_balance)

                    response.update(request.cart.get_result())
                    self.resp = response
                else:
                    request.cart.change_item_count(cart_item_obj.pk, new_product_count)

            except:
                self.resp = {'error': 'Произошла ошибка при изменении количества'}
