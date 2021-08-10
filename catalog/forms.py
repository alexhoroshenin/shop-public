from django import forms


class SearchForm(forms.Form):
    search_text = forms.CharField(label='Введите запрос', max_length=250, required=True)

