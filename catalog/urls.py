from django.urls import path, include
from . import views

app_name = 'catalog'

urlpatterns = [
    path('catalog/', views.ShowAllCategories.as_view()),
    path('catalog/<slug:slug>-<int:pk>/', views.CategoryIndex.as_view(), name='category_index'),
    path('product/<slug:slug>-<int:pk>/', views.ProductIndex.as_view()),
    path('search', views.SearchIndex.as_view(), name='search')
]
