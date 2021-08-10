from django.shortcuts import render, reverse, redirect
from django.db.models import Sum, F
from django.views import View
from .forms import LogOnForm, SignUpForm, AccountDetailForm, AccountChangePasswordForm
from django.contrib.auth import get_user_model, authenticate, login, logout
from .models import Profile
from django.db import IntegrityError
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import get_profile


class AccountIndex(LoginRequiredMixin, View):
    """Страница аккаунта пользователя"""
    def get(self, request):
        breadcrumbs = {'Мой аккаунт': reverse('account:index')}
        user = request.user
        form_account_details = AccountDetailForm()
        profile = get_profile(user)
        form_account_details = _fill_initial_values_in_detail_form(form_account_details, profile)

        return render(request,
                      'account.html',
                      {'breadcrumbs': breadcrumbs,
                       'orders': _get_orders(user),
                       'profile': profile,
                       'form_account_details': form_account_details})

    def post(self, request):
        user = request.user
        orders = _get_orders(user)
        profile = get_profile(user)
        breadcrumbs = {'Мой аккаунт': reverse('account:index')}

        if 'change_password_btn' in request.POST:
            form_change_password = AccountChangePasswordForm(request.POST)
            if form_change_password.is_valid():
                old_password = form_change_password.cleaned_data['old_password']
                authentificated_user = authenticate(request, username=user.email, password=old_password)

                if not authentificated_user:
                    form_change_password.general_errors = ['Старый пароль введен неверно.']
                    return render(request, 'account.html',
                                  {'breadcrumbs': breadcrumbs,
                                   'orders': orders,
                                   'profile': profile,
                                   'error': "Возникли ошибки при заполнении формы. Пароль не обновлен.",
                                   'form_change_password': form_change_password,
                                   'form_account_details': _fill_initial_values_in_detail_form(AccountDetailForm(), profile)
                                   })

                if authentificated_user:
                    new_password = form_change_password.cleaned_data['password1']
                    authentificated_user.set_password(new_password)
                    authentificated_user.save()

                    re_authentificated_user = authenticate(request, username=user.email, password=new_password)
                    if re_authentificated_user:
                        login(request, authentificated_user)

                    return render(request, 'account.html',
                                  {'breadcrumbs': breadcrumbs,
                                   'orders': orders,
                                   'profile': profile,
                                   'message': "Пароль успешно обновлен.",
                                   'form_change_password': form_change_password,
                                   'form_account_details': _fill_initial_values_in_detail_form(AccountDetailForm(), profile)
                                   })

            else:
                return render(request, 'account.html',
                              {'breadcrumbs': breadcrumbs,
                               'orders': orders,
                               'profile': profile,
                               'error': "Возникли ошибки при заполнении формы. Пароль не обновлен.",
                               'form_change_password': form_change_password,
                               'form_account_details': _fill_initial_values_in_detail_form(AccountDetailForm(), profile)
                               })


        elif 'account_details_btn' in request.POST:
            form_account_details = AccountDetailForm(request.POST)

            if form_account_details.is_valid():
                if not profile:
                    profile = _create_profile(user=user)

                profile.firstname = form_account_details.cleaned_data['firstname']
                profile.lastname = form_account_details.cleaned_data['lastname']
                profile.phone = form_account_details.cleaned_data['phone']
                profile.save()

                return render(request, 'account.html',
                              {'breadcrumbs': breadcrumbs,
                               'orders': _get_orders(user),
                               'profile': profile,
                               'message': "Контактная информация успешно обновлена",
                               'form_account_details': form_account_details})

            else:
                form_account_details.general_errors = ['Не заполнены обязательные поля.']
                return render(request, 'account.html',
                              {'breadcrumbs': breadcrumbs,
                               'orders': _get_orders(user),
                               'profile': profile,
                               'error': "Возникли ошибки при заполнении формы. Информация не обновлена.",
                               'form_account_details': form_account_details})

        return redirect(reverse('account:index'))


class LogOn(View):
    """Страница логина"""
    def get(self, request):
        form = LogOnForm()
        return render(request, 'logon.html', {'form': form})

    def post(self, request):
        form = LogOnForm(request.POST)
        next = request.GET.get('next')

        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            authentificated_user = authenticate(request, username=email, password=password)
            if authentificated_user:
                login(request, authentificated_user)
                if next:
                    return redirect(next)
                return redirect('/')

        form.add_error('email', 'Пользователь с такими email и паролем не найден. Повторите попытку.')
        return render(request, 'logon.html', {'form': form})


class LogOut(LoginRequiredMixin, View):
    """Контроллер разлогина"""
    def get(self, request):
        logout(request)
        return redirect('/')


class SignUp(View):
    """Страница регистрации"""
    def get(self, request):
        form = SignUpForm()
        return render(request, 'signup.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        next = request.GET.get('next')
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user, error = _create_user(email=email,
                                       username=email,
                                       password=password)

            if error:
                # Ошибка создания пользователя. Например, такой email уже занят или пароли не совпадают
                form.add_error('email', str(error))
                return render(request, 'signup.html', {'form': form})
            else:
                # Пользователь создан успешно. Авторизуем его.
                _create_profile(user=user,
                                phone=form.cleaned_data['phone'],
                                firstname=form.cleaned_data['firstname'],
                                lastname=form.cleaned_data['lastname'],
                                )
                authentificated_user = authenticate(request, username=email, password=password)
                if authentificated_user:
                    login(request, authentificated_user)
                    if next:
                        return redirect(next)
                    return redirect('/')
        else:
            # Неуспешная регистрация
            form.add_error('email', 'Ошибка регистрации пользователя. Попробуйте еще раз.')
            return render(request, 'signup.html', {'form': form})


def _create_user(email, username, password):
    user_model = get_user_model()

    user = None
    error = None

    with transaction.atomic():
        try:
            user = user_model.objects.create_user(email, username, password)

        except IntegrityError as e:
            if e.args and 'duplicate key' in e.args[0]:
                error = str('Пользователь с таким email уже зарегистрирован.')

        except Exception as e:
            error = str(e)

    return user, error


def _create_profile(user, phone=None, firstname=None, lastname=None):
    return Profile.objects.create(user=user, phone=phone, firstname=firstname, lastname=lastname)


def _fill_initial_values_in_detail_form(form, profile):
    if profile:
        form.fields['firstname'].initial = profile.firstname
        form.fields['lastname'].initial = profile.lastname
        form.fields['phone'].initial = profile.phone
    return form


def _get_orders(user):

    orders = user.order_set \
        .select_related('payment_method', 'delivery_method') \
        .prefetch_related('order_items') \
        .prefetch_related('order_items__product') \
        .prefetch_related('order_items__product__images') \
        .annotate(total=Sum(F('order_items__price') * F('order_items__quantity'))) \
        .order_by('-date_created')

    return orders

