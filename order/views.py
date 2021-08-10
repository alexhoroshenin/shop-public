from django.shortcuts import render, redirect, reverse, Http404
from order.forms import OrderForm
from cart.utils import get_active_cart
from cart.models import Cart
from catalog.models import StockBalance
from order.models import Order, Address, OrderItem, OrderItemToWarehose
from django.db.models import Sum, F, Q
from .utils import append_order_pk_into_session
from account.utils import get_profile, get_user_from_request
from django.views import View


class CreateOrder(View):

    def get(self, request):
        user = get_user_from_request(request)
        profile = get_profile(user)
        form = OrderForm()
        form = _fill_initial_values_in_order_form(form, profile)
        return render(request, 'create_order.html', {'form': form})

    def post(self, request):
        cart = get_active_cart(request)
        form = OrderForm(request.POST)
        user = get_user_from_request(request)

        if not form.is_valid():
            return render(request, 'create_order.html', {'form': form})

        if form.is_valid():
            state = form.cleaned_data['state']
            postcode = form.cleaned_data['postcode']
            city = form.cleaned_data['city']
            address_line = form.cleaned_data['address_line']

            if state or postcode or city or address_line:
                new_address = Address.objects.create(state=state,
                                                     postcode=postcode,
                                                     city=city,
                                                     address_line=address_line)
            else:
                new_address = None

            order = Order.objects.create(user=user,
                                         cart=cart,
                                         first_name=form.cleaned_data['first_name'],
                                         last_name=form.cleaned_data['last_name'],
                                         email=form.cleaned_data['email'],
                                         phone=form.cleaned_data['phone'],
                                         additional_info=form.cleaned_data['additional_info'],
                                         shipping_address=new_address,
                                         payment_method=cart.payment_method,
                                         delivery_method=cart.delivery_method,
                                         )

            # Списание товаров с баланса
            order_items = _create_order_items(order)
            _reserve_products_in_stock(order_items)

            cart.status = Cart.SUBMITTED
            cart.save()
            if not user:
                append_order_pk_into_session(request, order.pk)

            return redirect(reverse('order:show_order', kwargs={'pk': order.pk}))


class ShowOrder(View):

    def get(self, request, pk):

        user = get_user_from_request(request)

        if user:
            # Список заказов для авторизованного пользователя
            order_queryset = Order.objects.filter(pk=pk, user=user)
        else:
            # Список заказов для НЕавторизованного пользователя из сессии
            orders_from_session = request.session.get('order_list')
            if orders_from_session and pk in orders_from_session:
                order_queryset = Order.objects.filter(pk=pk)
            else:
                raise Http404('Заказ не найден.')

        order = order_queryset.prefetch_related('order_items') \
            .select_related('payment_method', 'delivery_method', 'shipping_address') \
            .prefetch_related('order_items__product') \
            .prefetch_related('order_items__product__images') \
            .annotate(total=Sum(F('order_items__price') * F('order_items__quantity')))

        order = order[0]

        breadcrumbs = {'Мой аккаунт': reverse('account:index'),
                       f'Заказ №{order.pk} от {order.date_created_str}': reverse('order:show_order',
                                                                                 kwargs={'pk': order.pk})}
        context = {'order': order, 'breadcrumbs': breadcrumbs}

        return render(request, 'order.html', context)


def compare_balance_with_order_quantity(cart):
    """Вернет список товаров с количество на складе меньшим, чем в заказе"""

    cart_items_with_shortage_of_goods = cart.cart_items.annotate(stock_balance=Sum('product__stockbalance__balance')) \
    .annotate(free_balance=F('stock_balance') - F('quantity')) \
    .filter(free_balance__lt=0)

    return list(cart_items_with_shortage_of_goods)


def _create_order_items(order):
    order_items = []
    for cart_item in order.cart.cart_items.all():
        quantity = cart_item.quantity
        product = cart_item.product
        price = cart_item.product.get_discount_price()
        order_item = OrderItem.objects.create(order=order,
                                             product=product,
                                             quantity=quantity,
                                             price=price)

        order_items.append(order_item)
    return order_items


def _reserve_products_in_stock(order_items):
    """Бронь остатков на складе для товаров из заказа"""

    for item in order_items:
        stockbalance = StockBalance.objects.select_for_update().filter(product=item.product, balance__gt=0).order_by('-balance')
        quantity = item.quantity

        for stock in stockbalance:
            if quantity <= 0:
                break

            if stock.balance >= item.quantity:
                # Если на данном складе количество товара больше, чем в заказе, то спишем количество из заказа
                stock.balance = F('balance') - quantity
                stock.save()
                subtracted_quantity = quantity
                quantity = 0

                OrderItemToWarehose.objects.create(orderitem=item,
                                                   warehouse=stock.warehouse,
                                                   subtracted_quantity=subtracted_quantity)

            elif stock.balance < item.quantity:
                # Если на данном складе количество меньше, чем в заказе, то спишем весь остаток и перейдем к следующему складу
                stock.balance = 0
                stock.save()
                quantity -= stock.balance

                OrderItemToWarehose.objects.create(orderitem=item,
                                                   warehouse=stock.warehouse,
                                                   subtracted_quantity=stock.balance)


def _fill_initial_values_in_order_form(form, profile):
    if profile:
        form.fields['first_name'].initial = profile.firstname
        form.fields['last_name'].initial = profile.lastname
        form.fields['phone'].initial = profile.phone
        form.fields['email'].initial = profile.user.email
    return form
