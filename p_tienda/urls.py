"""
URL configuration for p_tienda project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('caja/', include(('a_cajas.urls', 'a_cajas'), namespace='a_cajas')),
    path('cuenta/', include('a_login.urls')),
    path('', include('a_inicio.urls', namespace='a_inicio')),
    path('central/', include('a_central.urls', namespace='a_central')),
    path('stock/', include('a_stock.urls', namespace='a_stock')),
    path('cuenta/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('compras/', include(('a_compras.urls', 'a_compras'), namespace='a_compras')),
]

# En modo de desarrollo, sirve los archivos estáticos.
# Esta es una buena práctica para asegurar que CSS y JS se carguen correctamente.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)