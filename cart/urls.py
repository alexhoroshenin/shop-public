from django.urls import path, include
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartIndex.as_view(), name='index'),
    path('update-ajax', views.UpdateAjax.as_view()),
]
