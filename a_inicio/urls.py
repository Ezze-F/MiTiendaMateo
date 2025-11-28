from django.urls import path
from . import views

app_name = 'a_inicio'

urlpatterns = [
    path('', views.pagina_inicio, name='inicio'),
    path('terminos-y-condiciones/', views.terminos_y_condiciones, name='terminos_condiciones')

]