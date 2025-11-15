from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.conf import settings
from .forms import LoginForm
import random
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import ResetRequestForm, SecurityCodeForm, SetNewPasswordForm
from a_central.models import Empleados
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

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

# ====================================================
# VISTA DE AYUDA (Envío de Email Real)
# ====================================================
def send_security_code(email, code):
    """Envía el código de seguridad por correo usando la configuración de settings."""
    
    context = {'code': code}
    
    # Renderizar el contenido HTML del correo (usando la plantilla que crearemos)
    html_message = render_to_string('a_login/email/password_reset_code_email.html', context)
    # Generar la versión de texto plano para clientes que no soportan HTML
    plain_message = strip_tags(html_message)
    
    subject = 'Código de Seguridad para Restablecimiento de Contraseña'
    recipient_list = [email]

    try:
        send_mail(
            subject=subject,
            message=plain_message,  # Mensaje de texto plano
            from_email=None,        # Usa DEFAULT_FROM_EMAIL de settings.py
            recipient_list=recipient_list,
            html_message=html_message, # Mensaje HTML
            fail_silently=False,    # Lanza una excepción si falla el envío
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo electrónico: {e}")
        # Puedes agregar logging aquí.
        return False


# ====================================================
# 🔑 Paso 1, 2 y 3: Solicitud de Restablecimiento
# ====================================================
def password_reset_request(request):
    if request.method == 'POST':
        form = ResetRequestForm(request.POST)
        if form.is_valid():
            user_input = form.cleaned_data.get('username_or_email')
            
            # Buscar el usuario: por username o por email
            try:
                # 1. Intentar por username (case-insensitive)
                user = User.objects.get(username__iexact=user_input)
            except User.DoesNotExist:
                # 2. Intentar por email (asumiendo que el User de Django tiene el mismo email)
                try:
                    user = User.objects.get(email__iexact=user_input)
                except User.DoesNotExist:
                    # 3. No existe
                    messages.error(request, 'El usuario o email ingresado no existe.')
                    return render(request, 'a_login/password_reset_form.html', {'form': form})
            
            # El usuario existe (Paso 2 completado)
            
            # Generar código de 6 dígitos y guardarlo en sesión (Paso 3)
            security_code = str(random.randint(100000, 999999))
            
            # Guardamos el ID del usuario y el código en la sesión
            request.session['reset_user_id'] = user.id
            request.session['security_code'] = security_code
            
            # Obtener el email del modelo Empleados (mejor práctica)
            try:
                empleado = Empleados.objects.get(user_auth=user)
                email_to_send = empleado.email_emp
            except Empleados.DoesNotExist:
                # Si no está en Empleados, usamos el del modelo User (si lo tiene)
                email_to_send = user.email

            # Envío del código
            if send_security_code(email_to_send, security_code):
                messages.success(request, f'Se ha enviado un código de seguridad a su email ({email_to_send}).')
                return redirect('a_login:password_reset_code')
            else:
                # Si el envío falla
                messages.error(request, 'Error al enviar el código. Por favor, intente nuevamente más tarde.')
                return render(request, 'a_login/password_reset_form.html', {'form': form})
    else:
        # Limpiamos la sesión al iniciar el proceso
        if 'reset_user_id' in request.session:
            del request.session['reset_user_id']
        if 'security_code' in request.session:
            del request.session['security_code']
            
        form = ResetRequestForm()

    return render(request, 'a_login/password_reset_form.html', {'form': form})


# ====================================================
# 🔑 Paso 4: Ingreso del Código de Seguridad
# ====================================================
def password_reset_code(request):
    user_id = request.session.get('reset_user_id')
    stored_code = request.session.get('security_code')

    # Si no hay ID de usuario o código en la sesión, redirigimos al inicio
    if not user_id or not stored_code:
        messages.error(request, 'Debe iniciar el proceso de restablecimiento de contraseña.')
        return redirect('a_login:password_reset_request')

    if request.method == 'POST':
        form = SecurityCodeForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data.get('code')
            
            if entered_code == stored_code:
                # El código es correcto (Paso 4 completado)
                # Establecemos un flag de "código verificado" en la sesión
                request.session['code_verified'] = True
                messages.success(request, 'Código verificado. Ingrese su nueva contraseña.')
                return redirect('a_login:password_reset_new') # Ir al último paso
            else:
                messages.error(request, 'El código ingresado es incorrecto.')
                return render(request, 'a_login/password_reset_code.html', {'form': form})
    else:
        form = SecurityCodeForm()
        
    return render(request, 'a_login/password_reset_code.html', {'form': form})


# ====================================================
# 🔑 Paso 5: Colocar la Nueva Contraseña
# ====================================================
def password_reset_new(request):
    user_id = request.session.get('reset_user_id')
    code_verified = request.session.get('code_verified')
    
    # Verificamos que se haya pasado por los pasos anteriores
    if not user_id or not code_verified:
        messages.error(request, 'Proceso incompleto. Intente nuevamente.')
        # Limpiamos todo para empezar de cero
        if 'reset_user_id' in request.session: del request.session['reset_user_id']
        if 'security_code' in request.session: del request.session['security_code']
        if 'code_verified' in request.session: del request.session['code_verified']
        return redirect('a_login:password_reset_request')

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        messages.error(request, 'Error interno: Usuario no encontrado.')
        return redirect('a_login:password_reset_request')


    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data.get('new_password')
            
            # Cambiar la contraseña (función de Django que maneja el hashing)
            user.set_password(new_password)
            user.save()
            
            # Limpiamos la sesión después del éxito
            del request.session['reset_user_id']
            del request.session['security_code']
            del request.session['code_verified']

            messages.success(request, '¡Contraseña restablecida con éxito! Ya puedes iniciar sesión.')
            return redirect('a_login:login') # Redirigir al login principal
    else:
        form = SetNewPasswordForm()
        
    return render(request, 'a_login/password_reset_new.html', {'form': form})