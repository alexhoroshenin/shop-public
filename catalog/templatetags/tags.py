from django import template

register = template.Library()


@register.filter
def get_by_index(indexable, i):
    """Возвращает элемент по индексу"""
    try:
        return indexable[i]
    except:
        return None


@register.filter
def get_by_key(key_value_dict, key):
    """Возвращает элемент по индексу"""
    return key_value_dict.get(key)


@register.simple_tag
def GET_params_except_page(request):
    """Возвращает GET-параметры запроса"""
    get_params_str = ''

    for param, value in request.GET.items():
        if param != 'page':
            get_params_str += f"&{param}={value}"

    return get_params_str

