from django.contrib.auth.forms import AuthenticationForm
from django import forms


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
