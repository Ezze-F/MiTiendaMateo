from django.urls import path
from . import views

urlpatterns = [
    path('roles/', views.listar_roles, name='listar_roles'),
    path('roles/ingresar/', views.registrar_rol, name='registrar_rol'),
    path('roles/modificar/<int:pk>/', views.modificar_rol, name='modificar_rol'),
    path('roles/borrar/<int:pk>/', views.eliminar_rol, name='eliminar_rol'),
    path('roles/recuperar/<int:pk>/', views.recuperar_rol, name='recuperar_rol'),
]
