from django import forms


class ProcessCartForm(forms.Form):
    """Форма корзины"""

    payment_method = forms.ChoiceField(label='Способ оплаты', choices=[], widget=forms.Select(), required=False)
    delivery_method = forms.ChoiceField(label='Способ доставки', choices=[], widget=forms.Select(), required=False)
