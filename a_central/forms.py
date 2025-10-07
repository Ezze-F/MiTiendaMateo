from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from a_central.models import Empleados, Provincias


class EmpleadoRegistroForm(forms.Form):
    """
    Formulario personalizado para el registro de un Empleado.
    Ahora todos los campos son obligatorios, incluido 'usuario_emp'.
    """

    dni_emp = forms.IntegerField(
        required=True,
        label='DNI',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Sólo números'})
    )

    apellido_emp = forms.CharField(
        max_length=80,
        required=True,
        label='Apellido',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    nombre_emp = forms.CharField(
        max_length=80,
        required=True,
        label='Nombre',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email_emp = forms.EmailField(
        max_length=150,
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    telefono_emp = forms.CharField(
        max_length=20,
        required=True,
        label='Teléfono',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    domicilio_emp = forms.CharField(
        max_length=200,
        required=True,
        label='Domicilio',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    usuario_emp = forms.CharField(
        max_length=50,
        required=True,
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario único'})
    )

    contrasena_emp = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Contraseña Inicial'
    )

    contrasena_confirmacion = forms.CharField(
        max_length=128,
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='Confirmar Contraseña'
    )

    id_rol = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label='Rol/Grupo',
        widget=forms.Select(attrs={'class': 'form-control'}),
        empty_label="Seleccione un Rol"
    )

    # ================= VALIDACIONES ===================

    def clean_dni_emp(self):
        dni = self.cleaned_data.get('dni_emp')
        if Empleados.objects.filter(dni_emp=dni).exists():
            raise ValidationError("Ya existe un empleado con este DNI.")
        return dni

    def clean_usuario_emp(self):
        usuario = self.cleaned_data.get('usuario_emp')

        if Empleados.objects.filter(usuario_emp=usuario).exists():
            raise ValidationError("Este nombre de usuario ya está registrado en Empleados.")

        if User.objects.filter(username=usuario).exists():
            raise ValidationError("Este nombre de usuario ya está en uso en el sistema.")

        return usuario

    def clean_email_emp(self):
        email = self.cleaned_data.get('email_emp')
        if Empleados.objects.filter(email_emp=email).exists():
            raise ValidationError("Ya existe un empleado con este Email.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este Email ya está registrado en el sistema.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get('contrasena_emp')
        confirmacion = cleaned_data.get('contrasena_confirmacion')

        if contrasena and len(contrasena) < 8:
            self.add_error('contrasena_emp', "La contraseña debe tener al menos 8 caracteres.")

        if contrasena and confirmacion and contrasena != confirmacion:
            self.add_error('contrasena_confirmacion', "Las contraseñas no coinciden.")

        return cleaned_data


class ProvinciaForm(forms.ModelForm):
    class Meta:
        model = Provincias
        fields = ['nombre_provincia']
        widgets = {
            'nombre_provincia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: BUENOS AIRES',
                'maxlength': '50',
            })
        }

    def clean_nombre_provincia(self):
        nombre_provincia = self.cleaned_data.get('nombre_provincia')
        if not nombre_provincia:
            raise forms.ValidationError("El nombre de la provincia es obligatorio.")

        nombre_provincia_limpio = nombre_provincia.strip().upper()
        qs = Provincias.objects.filter(nombre_provincia__iexact=nombre_provincia_limpio)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(f"Ya existe una provincia con el nombre '{nombre_provincia_limpio}'.")

        return nombre_provincia_limpio

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.nombre_provincia = self.cleaned_data['nombre_provincia']
        if commit:
            instance.save()
        return instance
