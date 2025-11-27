from django.urls import path
from . import views

app_name = 'a_inicio'

urlpatterns = [
    path('inicio/', views.pagina_inicio, name='inicio'),
]