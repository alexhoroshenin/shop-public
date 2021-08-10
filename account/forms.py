from django.forms import ValidationError
from django import forms


class SignUpForm(forms.Form):
    """Форма регистрации"""
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=12, required=True)
    password1 = forms.CharField(max_length=100, required=True)
    password2 = forms.CharField(max_length=100, required=True)
    firstname = forms.CharField(max_length=100, required=True)
    lastname = forms.CharField(max_length=100, required=True)
    agree_with_personal_data_handling = forms.BooleanField(required=True)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise ValidationError('Пароли не совпадают')

        if len(password1) < 6:
            raise ValidationError('Слишком простой пароль. Длина пароля должна быть не менее 6 символов.')


class AccountDetailForm(forms.Form):
    """Форма изменения профиля"""
    phone = forms.CharField(max_length=12, required=True)
    firstname = forms.CharField(max_length=100, required=True)
    lastname = forms.CharField(max_length=100, required=True)


class AccountChangePasswordForm(forms.Form):
    """Форма смены пароля"""
    old_password = forms.CharField(max_length=100, required=True)
    password1 = forms.CharField(max_length=100, required=True)
    password2 = forms.CharField(max_length=100, required=True)

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise ValidationError('Пароли не совпадают')

        if len(password1) < 6:
            raise ValidationError('Слишком простой пароль. Длина пароля должна быть не менее 6 символов.')


class LogOnForm(forms.Form):
    """Форма авторизации"""
    email = forms.EmailField(required=True)
    password = forms.CharField(max_length=100, required=True)
