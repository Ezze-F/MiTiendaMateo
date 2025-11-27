from django.urls import path
from . import views
from .views import obtener_stock_minimo

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
    path('provincias/disponibles/', views.provincias_disponibles_api, name='provincias_disponibles_api'),
    path('provincias/eliminadas/', views.provincias_eliminadas_api, name='provincias_eliminadas_api'),   
    path('provincias/registrar/', views.registrar_provincia, name='registrar_provincia'),               
    path('provincias/modificar/<int:provincia_id>/', views.modificar_provincia, name='modificar_provincia'), 
    path('provincias/borrar/<int:provincia_id>/', views.borrar_provincia, name='borrar_provincia'),           
    path('provincias/recuperar/<int:provincia_id>/', views.recuperar_provincia, name='recuperar_provincia'),
    # ==================================
    # RUTAS DE MARCAS
    # ==================================
    path('marcas/', views.listar_marcas, name='listar_marcas'), 
    path('marcas/disponibles/', views.marcas_disponibles_api, name='marcas_disponibles_api'),
    path('marcas/eliminadas/', views.marcas_eliminadas_api, name='marcas_eliminadas_api'),
    path('marcas/registrar/', views.registrar_marca, name='registrar_marca'),
    path('marcas/modificar/<int:marca_id>/', views.modificar_marca, name='modificar_marca'),
    path('marcas/borrar/<int:marca_id>/', views.borrar_marca, name='borrar_marca'),
    path('marcas/recuperar/<int:marca_id>/', views.recuperar_marca, name='recuperar_marca'),
    # ==================================
    # RUTAS DE PROVEEDORES
    # ==================================
    path('proveedores/', views.listar_proveedores, name='listar_proveedores'),
    path('proveedores/disponibles/', views.proveedores_disponibles_api, name='proveedores_disponibles_api'), 
    path('proveedores/eliminados/', views.proveedores_eliminados_api, name='proveedores_eliminados_api'),
    path('proveedores/registrar/', views.registrar_proveedor, name='registrar_proveedor'),
    path('proveedores/modificar/<int:proveedor_id>/', views.modificar_proveedor, name='modificar_proveedor'),
    path('proveedores/borrar/<int:proveedor_id>/', views.borrar_proveedor, name='borrar_proveedor'),
    path('proveedores/recuperar/<int:proveedor_id>/', views.recuperar_proveedor, name='recuperar_proveedor'),
    path('proveedores/cargar-datos/<int:proveedor_id>/', views.cargar_datos_proveedor, name='cargar_datos_proveedor'),
    # ==================================
    # RUTAS DE LOCALES COMERCIALES
    # ==================================
    path('locales/', views.listar_locales, name='listar_locales'),
    path('locales/disponibles/', views.locales_disponibles_api, name='locales_disponibles_api'),
    path('locales/eliminados/', views.locales_eliminados_api, name='locales_eliminados_api'),
    path('locales/registrar/', views.registrar_local, name='registrar_local'),
    path('locales/modificar/<int:local_id>/', views.modificar_local, name='modificar_local'),
    path('locales/borrar/<int:local_id>/', views.borrar_local, name='borrar_local'),
    path('locales/recuperar/<int:local_id>/', views.recuperar_local, name='recuperar_local'),
    # ==================================
    # RUTAS DE PRODUCTOS
    # ==================================    
    path('productos/', views.listar_productos, name='listar_productos'),
    path('productos/disponibles/', views.productos_disponibles_api, name='productos_disponibles_api'),
    path('productos/eliminados/', views.productos_eliminados_api, name='productos_eliminados_api'),
    path('productos/registrar/', views.registrar_producto, name='registrar_producto'),
    path('productos/modificar/<int:producto_id>/', views.modificar_producto, name='modificar_producto'),
    path('productos/borrar/<int:producto_id>/', views.borrar_producto, name='borrar_producto'),
    path('productos/recuperar/<int:producto_id>/', views.recuperar_producto, name='recuperar_producto'),
    path('stock/minimo/<int:producto_id>/<int:id_loc_com>/', views.obtener_stock_minimo, name='obtener_stock_minimo'),

    # ==================================
    # RUTAS DE PRODUCTOS
    # ==================================
    path('billeteras/', views.listar_billeteras, name='listar_billeteras'),
    path('billeteras/disponibles/', views.billeteras_disponibles_api, name='billeteras_disponibles_api'),
    path('billeteras/eliminados/', views.billeteras_eliminadas_api, name='billeteras_eliminadas_api'),
    path('billeteras/registrar/', views.registrar_billetera, name='registrar_billetera'),
    path('billeteras/modificar/<int:billetera_id>/', views.modificar_billetera, name='modificar_billetera'),
    path('billeteras/borrar/<int:billetera_id>/', views.borrar_billetera, name='borrar_billetera'),
    path('billeteras/recuperar/<int:billetera_id>/', views.recuperar_billetera, name='recuperar_billetera'),
]