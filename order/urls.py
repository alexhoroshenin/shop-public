from django.urls import path, include
from . import views

app_name = 'order'

urlpatterns = [
    path('create_order/', views.CreateOrder.as_view(), name='create_order'),
    path('<int:pk>/', views.ShowOrder.as_view(), name='show_order'),
]
