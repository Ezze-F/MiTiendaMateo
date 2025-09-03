from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.listar_prod, name='listar_prod'),
]
#     path('listar/', views.listar_prod, name='listar_prod'), # "listar/" es la ruta donde se carga la funcionalidad "listrar_productos" del views.py con el nombre "listar_prod"
#     path('registrar/', views.ingresar_prod, name='ingresar_prod'), # "registrar/" es la ruta donde se carga la funcionalidad "registrar_producto" del views.py con el nombre "registrar_prod"
#     path('<int:pk>/modificar/', views.editar_prod, name='editar_prod'), # "modificar/" es la ruta donde se carga la funcionalidad "modificar_producto" del views.py con el nombre "modificar_prod". Se le pasa pk para que la funcionalidad trabaje con ella.
#     path('<int:pk>/eliminar/', views.eliminar_producto, name='eliminar_prod'), # "eliminar/" es la ruta donde se carga la funcionalidad "eliminar_producto" del views.py con el nombre "eliminar_prod". Se le pasa pk para que la funcionalidad trabaje con ella.
#     path('<int:pk>/restaurar/', views.restaurar_producto, name='restaurar_prod'), # "restaurar/" es la ruta donde se carga la funcionalidad "restaurar_producto" del views.py con el nombre "restaurar_prod"
