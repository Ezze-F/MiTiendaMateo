from django.urls import path
from . import views

app_name = 'a_compras'

urlpatterns = [
    path('', views.listar_compras, name='listar_compras'),
    path('eliminar/<int:pk>/', views.eliminar_compra, name='eliminar_compra'),
    path('detalle/<int:pk>/', views.detalle_compra, name='detalle_compra'),
    path('pedidos_provisorios/', views.listar_pedidos_provisorios, name='listar_pedidos_provisorios'),
    
        # NUEVAS RUTAS
    path('pedidos_provisorios/detalle/<int:pk>/', views.detalle_pedido_provisorio, name='detalle_pedido_provisorio'),
    path('pedidos_provisorios/confirmar/<int:pk>/', views.confirmar_pedido_provisorio, name='confirmar_pedido_provisorio'),
    path('pedidos/generar-automaticos/', views.generar_pedidos_automaticos, name='generar_pedidos_automaticos'),
    path('ajax/locales-productos/<int:proveedor_id>/', views.ajax_locales_productos, name='ajax_locales_productos'),
    path('ajax/proveedores-local/<int:local_id>/', views.ajax_proveedores_por_local, name='ajax_proveedores_por_local'),
    path("registrar-pago/<int:compra_id>/", views.registrar_pago, name="registrar_pago"),
    path("ajax/billeteras/", views.ajax_billeteras, name="ajax_billeteras"),
    path('orden-pdf/<int:compra_id>/', views.generar_orden_pdf, name='generar_orden_pdf'),
    path('pedidos_provisorios/', views.listar_pedidos_provisorios, name='listar_pedidos_provisorios'),
]
