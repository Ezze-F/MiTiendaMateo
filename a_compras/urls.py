from django.urls import path
from . import views

app_name = 'a_compras'

urlpatterns = [
    path('', views.listar_compras, name='listar_compras'),
    path('eliminar/<int:pk>/', views.eliminar_compra, name='eliminar_compra'),
    path('detalle/<int:pk>/', views.detalle_compra, name='detalle_compra'),
    path('pedidos_provisorios/', views.listar_pedidos_provisorios, name='listar_pedidos_provisorios'),

]
