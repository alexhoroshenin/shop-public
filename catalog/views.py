from django.shortcuts import render, get_object_or_404, redirect, reverse, HttpResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Sum, Value, Case, When, IntegerField, BooleanField, Q
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.views.decorators.cache import cache_page
from django.utils import timezone
from django.views import View
from django.utils.decorators import method_decorator
from .forms import SearchForm
from .models import Product, Category


class CategoryIndex(View):

    def get(self, request, slug, pk):
        category_obj = get_object_or_404(Category, pk=pk, slug=slug)
        category_with_children = category_obj.get_descendants(include_self=True)
        breadcrumbs = _get_breadcrumbs_of_category(category_obj, include_self=True)

        ordering = request.GET.get('ordering')
        order_by_list = self._get_ordering_conditions(ordering)

        product_list = \
            Product.objects.filter(
                Q(optional_category__in=category_with_children) | Q(main_category__in=category_with_children)) \
                .prefetch_related('images') \
                .annotate(balance=Sum('stockbalance__balance')) \
                .annotate(plus_balance=Case(When(balance__gt=0, then=Value('1')), default=Value('0'),
                                            output_field=IntegerField())) \
                .annotate(active_discount=Case(When(discount_finish_date__gte=timezone.now(), then=Value(True)),
                                               default=Value(False),
                                               output_field=BooleanField())) \
                .order_by(*order_by_list) \
                .distinct()

        paginator = Paginator(product_list, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'breadcrumbs': breadcrumbs,
            'page_obj': page_obj,
            'default_image': settings.DEFAULT_PRODUCT_IMAGE,
            'title': category_obj.name,
            'ordering': ordering
        }

        return render(request, 'category.html', context=context)

    def _get_ordering_conditions(self, ordering):
        """Возвращает список условий для сортировки товаров в категории"""
        order_by_conditions = ['-plus_balance']

        if ordering == 'relevance':
            pass
        elif ordering == 'by_name':
            order_by_conditions.append('name')
        elif ordering == 'price_low':
            order_by_conditions.append('price')
        elif ordering == 'price_height':
            order_by_conditions.append('-price')

        return order_by_conditions


class ShowAllCategories(View):

    def get(self, request):
        return render(request, 'category.html')


class ProductIndex(View):

    def get(self, request, slug, pk):
        product = get_object_or_404(Product, pk=pk, slug=slug)
        optional_categories_pk = [cat.id for cat in product.optional_category.all()]
        main_category = self._get_main_category(product, optional_categories_pk)
        breadcrumbs = self._create_breadcrumbs(main_category)

        similar_products = self._get_similar_products(main_category, optional_categories_pk)

        context = {
            'product': product,
            'images': product.images.all(),
            'breadcrumbs': breadcrumbs,
            'similar_products': similar_products,
            'count_in_cart': self._get_count_of_product_in_cart(request, product),
            'balance': product.get_balance()
        }

        return render(request, 'product.html', context)

    def _get_main_category(self, product, optional_categories_pk):
        """Возвращает основную категорию товара. Если не указана Основная категория, вернет наиболее старую опциональную.
        Если не указаны доп категории, вернет None"""
        if product.main_category:
            return product.main_category

        if not product.main_category and len(optional_categories_pk) > 0:
            main_category_pk = min(optional_categories_pk)
            main_category = Category.objects.get(pk=main_category_pk)
            return main_category

        return None

    def _create_breadcrumbs(self, main_category):
        """Возвращает хлебные крошки"""
        if main_category:
            return _get_breadcrumbs_of_category(main_category, include_self=True)
        return None

    def _get_count_of_product_in_cart(self, request, product):
        """Возвращает количество товара в корзине"""
        if request.cart:
            return request.cart.get_count_of_product_by_product_obj(product)
        return 0

    def _get_similar_products(self, main_category, optional_categories_pk):
        """Возвращает список похожих товаров"""
        similar_products = \
            Product.objects \
                .prefetch_related('images') \
                .annotate(balance=Sum('stockbalance__balance')) \
                .annotate(plus_balance=Case(When(balance__gt=0, then=Value('1')), default=Value('0'),
                                            output_field=IntegerField())) \
                .filter(balance__gt=0) \
                .order_by('-plus_balance') \
                .distinct()


        if main_category:
            similar_categores = [main_category.pk] + optional_categories_pk
            similar_products.filter(Q(optional_category__pk__in=similar_categores) |
                                    Q(main_category__pk__in=similar_categores))

        elif not main_category and len(optional_categories_pk) > 0:
            similar_products.filter(Q(optional_category__pk__in=optional_categories_pk) |
                                    Q(main_category__pk__in=optional_categories_pk))

        similar_product_list = [p for p in similar_products[:12]]

        return similar_product_list


@method_decorator(cache_page(timeout=60), name='dispatch')
class SearchIndex(View):

    def get(self, request):
        search_text_get = request.GET.get('search')
        context = {'title': 'Поиск по сайту'}
        if search_text_get:
            product_list = _get_search_result(search_text_get)
            paginator = Paginator(product_list, 20)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            context.update({'page_obj': page_obj})
        return render(request, 'search.html', context)

    def post(self, request):
        context = {'title': 'Поиск по сайту'}
        form = SearchForm(request.POST)
        if form.is_valid():
            search_text_form = form.cleaned_data['search_text']
            target_url = reverse('catalog:search') + f"?search={search_text_form}"

            return redirect(target_url)

        return render(request, 'search.html', context)


def _get_search_result(search_text):

    vector = SearchVector('name')
    query = SearchQuery(search_text, search_type='websearch')
    product_list = Product.objects.annotate(rank=SearchRank(vector, query)) \
                    .prefetch_related('images') \
                    .annotate(balance=Sum('stockbalance__balance')) \
                    .annotate(active_discount=Case(When(discount_finish_date__gte=timezone.now(), then=Value(True)),
                                                      default=Value(False),
                                                      output_field=BooleanField())) \
                    .annotate(plus_balance=Case(When(balance__gt=0, then=Value('1')), default=Value('0'),
                                                   output_field=IntegerField())) \
                    .filter(rank__gt=0.001) \
                    .order_by('-rank') \
                    .distinct()

    return product_list



def _get_breadcrumbs_of_category(category, include_self=False):
    category_with_parents = category.get_ancestors(ascending=False, include_self=include_self)
    breadcrumbs = {}
    for cat in category_with_parents:
        breadcrumbs[cat.name] = cat.get_full_url()

    return breadcrumbs
