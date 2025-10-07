from django.urls import path
from . import views

app_name = 'a_login' 

urlpatterns = [
    # Mapea la URL 'login/' a la vista login_view
    path('login/', views.login_view, name='login'),
]
