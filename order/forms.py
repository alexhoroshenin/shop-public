from django import forms


class OrderForm(forms.Form):
    """Форма оформления заказа"""

    first_name = forms.CharField(label='Имя (обязательно)', max_length=100, required=True)
    last_name = forms.CharField(label='Фамилия (обязательно)', max_length=100, required=True)
    email = forms.CharField(label='Email (обязательно)', max_length=50, required=True)
    phone = forms.CharField(label='Телефон (обязательно)', max_length=12, required=True)

    state = forms.CharField(label='Область/Край', max_length=128, required=False)
    city = forms.CharField(label='Город', max_length=128, required=False)
    postcode = forms.CharField(label='Индекс', max_length=64, required=False)
    address_line = forms.CharField(label='Адрес', max_length=256, required=False)

    additional_info = forms.CharField(label='Дополнительная информация или комментарий', max_length=500, required=False)
    create_account = forms.BooleanField(label='Создать аккаунт', required=False)
