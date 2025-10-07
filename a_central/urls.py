from django.urls import path
from . import views

app_name = 'a_central'

urlpatterns = [
    # ==================================
    # RUTAS DE EMPLEADOS
    # ==================================
    path('empleados/', views.listar_empleados, name='listar_empleados'), 
    path('empleados/disponibles/', views.empleados_disponibles_api, name='empleados_disponibles_api'),
    path('empleados/eliminados/', views.empleados_eliminados_api, name='empleados_eliminados_api'),   
    path('empleados/registrar/', views.registrar_empleado, name='registrar_empleado'),               
    path('empleados/modificar/<int:empleado_id>/', views.modificar_empleado, name='modificar_empleado'), 
    path('empleados/borrar/<int:empleado_id>/', views.borrar_empleado, name='borrar_empleado'),           
    path('empleados/recuperar/<int:empleado_id>/', views.recuperar_empleado, name='recuperar_empleado'), 

    # ==================================
    # RUTAS DE PROVINCIAS
    # ==================================
    path('provincias/', views.listar_provincias, name='listar_provincias'),
    
    # APIs de DataTables (GET)
    path('provincias/activas/', views.provincias_activas_api, name='provincias_activas_api'),
    path('provincias/eliminadas/', views.provincias_eliminadas_api, name='provincias_eliminadas_api'),
    
    # APIs de CRUD (POST)
    path('provincias/registrar/', views.registrar_provincia, name='registrar_provincia'),
    path('provincias/modificar/<int:provincia_id>/', views.modificar_provincia, name='modificar_provincia'),
    path('provincias/borrar/<int:provincia_id>/', views.borrar_provincia, name='borrar_provincia'),
    path('provincias/recuperar/<int:provincia_id>/', views.recuperar_provincia, name='recuperar_provincia'),
]