from django.urls import path
from . import views

app_name = 'a_login' 

urlpatterns = [
    # Mapea la URL 'login/' a la vista login_view
    path('', views.login_view, name='login'),
    path('password_reset/', views.password_reset_request, name='password_reset_request'),
    
    # URL para ingresar el código
    path('password_reset/code/', views.password_reset_code, name='password_reset_code'),
    
    # URL para ingresar la nueva contraseña
    path('password_reset/new/', views.password_reset_new, name='password_reset_new'),
]