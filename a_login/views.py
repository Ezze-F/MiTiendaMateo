from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.conf import settings
from .forms import LoginForm


def login_view(request):
    """
    Vista para manejar el inicio de sesión.
    Solo se permite ingresar mediante el 'usuario_emp' y la contraseña correspondiente.
    """
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.error(request, "Credenciales incorrectas o usuario inactivo.")
        else:
            messages.error(request, "Error de inicio de sesión. Verifica tus datos.")
    else:
        form = LoginForm()

    return render(request, 'a_login/login.html', {'form': form})
