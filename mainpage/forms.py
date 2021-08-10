from django import forms


class ContactForm(forms.Form):
    """Форма обратной связи"""
    name = forms.CharField(label='Ваше имя', max_length=250, required=True)
    phone = forms.CharField(label='Телефон для связи', max_length=12, required=False)
    text = forms.CharField(label='Сообщение', widget=forms.Textarea)
