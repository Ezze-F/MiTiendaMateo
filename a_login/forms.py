from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    """
    Formulario de autenticación personalizado.
    No muestra mensajes de error por defecto de Django.
    """

    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Introduce tu nombre de usuario'
        }),
        max_length=150
    )

    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
    )

    class Meta:
        fields = ['username', 'password']

    # 🔹 Sobrescribimos el método para eliminar errores automáticos
    def confirm_login_allowed(self, user):
        """Evita los errores por usuario inactivo o inválido."""
        pass

    def add_error(self, field, error):
        """
        Anulamos los errores automáticos de Django.
        Esto evita que se muestren los 'non_field_errors()' predeterminados.
        """
        # Solo agregamos errores si es un campo, no globales
        if field:
            super().add_error(field, error)

    def non_field_errors(self):
        """Devuelve lista vacía (oculta mensajes globales)."""
        return self.error_class([])


# ====================================================
# Etapa 1: Ingreso de Usuario/Email
# ====================================================
class ResetRequestForm(forms.Form):
    # Se recomienda usar email, pero si el usuario es más común, se usa este
    username_or_email = forms.CharField(
        label='Usuario o Email',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese su usuario o email'})
    )

# ====================================================
# Etapa 4: Ingreso del Código de Seguridad
# ====================================================
class SecurityCodeForm(forms.Form):
    code = forms.CharField(
        label='Código de Seguridad',
        max_length=6, # Suponiendo un código de 6 dígitos
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese el código de 6 dígitos'})
    )

# ====================================================
# Etapa 5: Ingreso de la Nueva Contraseña
# ====================================================
class SetNewPasswordForm(forms.Form):
    new_password = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Nueva contraseña'})
    )
    confirm_password = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirme la contraseña'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data