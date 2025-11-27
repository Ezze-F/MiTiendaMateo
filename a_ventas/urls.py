from django.urls import path
from . import views

app_name = 'a_ventas'

urlpatterns = [
    path('', views.listar_ventas, name='listar_ventas'),
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    path('detalle/<int:venta_id>/', views.detalle_venta, name='detalle_venta'),
    path('anular/<int:venta_id>/', views.anular_venta, name='anular_venta'),
    path('api/productos/', views.productos_disponibles_api, name='productos_disponibles_api'),
    path('api/stock/<int:producto_id>/<int:local_id>/', views.verificar_stock_api, name='verificar_stock_api'),
    path('api/cajas-disponibles/<int:local_id>/', views.cajas_disponibles_api, name='cajas_disponibles_api'),
    path('cierre-caja/', views.cierre_caja, name='cierre_caja'),
    path('api/ventas-del-dia/', views.ventas_del_dia_api, name='ventas_del_dia_api'),
    # Nueva URL para el ticket
    path('ticket/<int:venta_id>/', views.imprimir_ticket, name='imprimir_ticket'),
]