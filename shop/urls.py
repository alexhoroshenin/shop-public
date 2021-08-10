from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.flatpages import views


urlpatterns = [
    path('', include('mainpage.urls')),
    path('', include('catalog.urls')),
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls')),
    path('order/', include('order.urls')),
    path('account/', include('account.urls')),
    path('api/', include('api.urls')),

    # FlatPages
    path('about/', views.flatpage, {'url': '/about/'}, name='about'),
    path('delivery/', views.flatpage, {'url': '/delivery/'}, name='delivery'),
    path('return/', views.flatpage, {'url': '/return/'}, name='return'),
    path('policy/', views.flatpage, {'url': '/policy/'}, name='policy'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
