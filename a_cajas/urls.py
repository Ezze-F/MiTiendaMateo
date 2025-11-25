from django.urls import path
from . import views

app_name = 'a_cajas'

urlpatterns = [
    # Vistas de listado y CRUD
    path('cajas/', views.listar_cajas, name='listar_cajas'),
    path('cajas/registrar/', views.registrar_caja, name='registrar_caja'),
    path('cajas/modificar/<int:caja_id>/', views.modificar_caja, name='modificar_caja'),
    path('cajas/borrar/<int:caja_id>/', views.borrar_caja, name='borrar_caja'),
    path('cajas/recuperar/<int:caja_id>/', views.recuperar_caja, name='recuperar_caja'),

    # NUEVAS VISTAS DE ESTADO
    path('cajas/abrir/<int:caja_id>/', views.abrir_caja, name='abrir_caja'),
    path('cajas/cerrar/<int:caja_id>/', views.cerrar_caja, name='cerrar_caja'),

    # Vistas API
    path('cajas/disponibles/', views.cajas_disponibles_api, name='cajas_disponibles_api'),
    path('cajas/eliminadas/', views.cajas_eliminadas_api, name='cajas_eliminadas_api'),
    # NUEVA VISTA API PARA ARQUEOS
    path('cajas/arqueos/', views.arqueos_api, name='arqueos_api'),
    path('cajas/apertura/<int:caja_id>/', views.registrar_apertura_caja, name='registrar_apertura_caja'),
    path('cajas/cierre/<int:caja_id>/', views.registrar_cierre_caja, name='registrar_cierre_caja'),
    path('cajas/arqueo-activo/<int:caja_id>/', views.obtener_arqueo_abierto_api, name='obtener_arqueo_abierto_api'),

]