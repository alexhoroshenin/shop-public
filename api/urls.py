from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('exchange', views.exchange),
    path('handle-test', views.handle_exchange_test),
    # path('load-json/', views.load_json, name='load_json'),
]
