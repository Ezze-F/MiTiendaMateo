from django.urls import path
from . import views

app_name = 'a_central'

urlpatterns = [
    # Muestra la página principal de roles
    path('roles/', views.listar_roles, name='listar_roles'),
    
    # Rutas para los datos de la API de roles (corregidas para coincidir con roles.js)
    path('roles/disponibles/', views.roles_disponibles_data, name='roles_disponibles_data'),
    path('roles/eliminados/', views.roles_eliminados_data, name='roles_eliminados_data'),
    
    # Rutas para las operaciones de CRUD de roles
    path('registrar/', views.registrar_rol, name='registrar_rol'),
    path('modificar/<int:rol_id>/', views.modificar_rol, name='modificar_rol'),
    path('borrar/<int:rol_id>/', views.borrar_rol, name='borrar_rol'),
    path('recuperar/<int:rol_id>/', views.recuperar_rol, name='recuperar_rol'),
]