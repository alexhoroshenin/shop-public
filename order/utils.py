def get_str_date(date):
    """Дата в формате 01.01.2021"""
    return f"{date.day:02d}.{date.month:02d}.{date.year}"


def append_order_pk_into_session(request, order_pk):
    """добавляет id заказа в сессию"""
    order_list = request.session.get('order_list')
    if order_list:
        order_list.append(order_pk)
        request.session['order_list'] = order_list
    else:
        request.session['order_list'] = [order_pk]
