from django.urls import path
from . import views

app_name = 'a_stock'

urlpatterns = [
    # ---- Observaciones ----
    path("observaciones/", views.lista_observaciones, name="lista_observaciones"),
    path("observaciones/nueva/", views.registrar_observacion, name="registrar_observacion"),
    path("observaciones/eliminar/<int:id>/", views.eliminar_observacion, name="eliminar_observacion"),

    # ---- Stock ----
    path('stock/', views.lista_stock, name='lista_stock'),
    path('stock/nuevo/', views.nuevo_stock, name='nuevo_stock'),
    path('stock/editar/<int:id>/', views.editar_stock, name='editar_stock'),
    path('stock/eliminar/<int:id>/', views.eliminar_stock, name='eliminar_stock'),
    path('api/stock/', views.obtener_stock_json, name='obtener_stock_json'),

    # ---- Lotes ----
    path('lotes/<int:id_producto>/', views.ver_lotes, name='ver_lotes'),
    path('lotes/<int:id_producto>/nuevo/', views.nuevo_lote, name='nuevo_lote'),
    path('lotes/editar/<int:id_lote>/', views.editar_lote, name='editar_lote'),
    path('lotes/eliminar/<int:id_lote>/', views.eliminar_lote, name='eliminar_lote'),
    path('lotes/reactivar/<int:id_lote>/', views.reactivar_lote, name='reactivar_lote'),

    # ---- Cargar compras → crear lotes ----
    path('cargar-compras/', views.cargar_compras, name='cargar_compras'),
    path('procesar-compra/<int:compra_id>/', views.procesar_compra_en_stock, name='procesar_compra_en_stock'),
]
