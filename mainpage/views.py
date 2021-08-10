from django.shortcuts import render, HttpResponseRedirect, reverse, redirect, get_object_or_404
from catalog.models import Product, ProductImage
from django.db.models import Sum, Prefetch, Case, When, Value, BooleanField, IntegerField
from .forms import ContactForm
from .models import ClientMessage, Banner
from django.utils import timezone
from django.views import View
from django.db import connection


class MainPageIndex(View):
    """Главная страница"""
    def get(self, request):
        products = \
            Product.objects \
                .annotate(balance=Sum('stockbalance__balance')) \
                .annotate(plus_balance=Case(When(balance__gt=0, then=Value('1')), default=Value('0'),
                                            output_field=IntegerField())) \
                .filter(balance__gt=0) \
                .annotate(active_discount=Case(When(discount_finish_date__gte=timezone.now(), then=Value(True)),
                                               default=Value(False),
                                               output_field=BooleanField())) \
                .order_by('-plus_balance') \
                .prefetch_related('images')

        products = list(products)

        # Показываем 3 баннера в блоке или ни одного
        banners = list(Banner.objects.filter(show=True))
        banners_block_1 = banners[0:3] if len(banners) >= 3 else []
        banners_block_2 = banners[4:6] if len(banners) >= 6 else []

        context = {
            'products_for_block_1': products[0:8],
            'products_for_block_2': products[8:16],
            'products_for_block_3': products[16:24],
            'banners_block_1': banners_block_1,
            'banners_block_2': banners_block_2,
        }

        return render(request, 'main.html', context)


class Contact(View):
    """Страница обратной связи"""
    def get(self, request):
        form = ContactForm()
        return render(request, 'contact.html', {'form': form})

    def post(self, request):
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            text = form.cleaned_data['text']
            user = request.user if request.user.is_authenticated else None

            client_message = ClientMessage.objects.create(name=name, phone=phone, text=text, user=user)

            return redirect(reverse('mainpage:contact_thx', kwargs={'pk': client_message.pk}))
        else:
            return render(request, 'contact.html', {'form': form})


class ContactThx(View):
    """Страница благодарности за останвленное сообщение"""
    def get(self, request, pk):
        client_message = get_object_or_404(ClientMessage, pk=pk)
        return render(request, 'contact_thx.html', {'client_message': client_message})
