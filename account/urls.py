from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('', views.AccountIndex.as_view(), name='index'),
    path('logon', views.LogOn.as_view(), name='logon'),
    path('logout', views.LogOut.as_view(), name='logout'),
    path('signup', views.SignUp.as_view(), name='signup'),
]
