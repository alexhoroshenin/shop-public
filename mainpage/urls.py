from django.urls import path
from . import views

app_name = 'mainpage'

urlpatterns = [
    path('', views.MainPageIndex.as_view(), name='main_page'),
    path('contact/', views.Contact.as_view(), name='contact'),
    path('contact-thx/<int:pk>', views.ContactThx.as_view(), name='contact_thx'),
]
