from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group
from .models import Empleados, Provincias, Marcas, Proveedores, LocalesComerciales, Productos, BilleterasVirtuales


class EmpleadoRegistroForm(forms.Form):
    # ... (Campos de formulario sin modificar) ...
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

    def clean_dni_emp(self):
        dni = self.cleaned_data.get('dni_emp')
        # Buscamos en TODOS los empleados (activos e inactivos)
        if Empleados.all_objects.filter(dni_emp=dni).exists():
            raise ValidationError("Ya existe un empleado con este DNI (activo o inactivo).")
        return dni

    def clean_usuario_emp(self):
        usuario = self.cleaned_data.get('usuario_emp')

        # Buscamos en TODOS los empleados (activos e inactivos)
        if Empleados.all_objects.filter(usuario_emp=usuario).exists():
            raise ValidationError("Este nombre de usuario ya está registrado en Empleados (activo o inactivo).")

        if User.objects.filter(username=usuario).exists():
            raise ValidationError("Este nombre de usuario ya está en uso en el sistema (tabla User).")

        return usuario

    def clean_email_emp(self):
        email = self.cleaned_data.get('email_emp')
        # Buscamos en TODOS los empleados (activos e inactivos)
        if Empleados.all_objects.filter(email_emp=email).exists():
            raise ValidationError("Ya existe un empleado con este Email (activo o inactivo).")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este Email ya está registrado en el sistema (tabla User).")
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


# ===============================================
# FORMULARIO PROVINCIAS
# ===============================================

class ProvinciaForm(forms.ModelForm):
    """Formulario para registrar/modificar una Provincia."""
    nombre_provincia = forms.CharField(
        label='Nombre de la provincia',
        error_messages={'required': 'El nombre de la provincia es obligatorio.'}
    )

    class Meta:
        model = Provincias
        fields = ['nombre_provincia']
        widgets = {
            'nombre_provincia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la Provincia'}),
        }
        labels = {
            'nombre_provincia': 'Nombre de la Provincia',
        }

    def clean_nombre_provincia(self):
        nombre = self.cleaned_data.get('nombre_provincia')
        # Limpieza para manejar mayúsculas/minúsculas
        nombre_limpio = nombre.strip().capitalize()
        
        # Obtener el ID de la instancia si estamos editando
        instance_id = self.instance.pk
        
        # Validar unicidad usando all_objects para incluir borrados lógicamente
        queryset = Provincias.all_objects.filter(nombre_provincia__iexact=nombre_limpio)
        
        if instance_id:
            # Excluir la instancia actual si estamos editando
            queryset = queryset.exclude(pk=instance_id)

        if queryset.exists():
            raise ValidationError("Ya existe una provincia con este nombre.")
            
        return nombre_limpio


# ===============================================
# FORMULARIO MARCAS
# ===============================================

class MarcaForm(forms.ModelForm):
    """Formulario para registrar/modificar una Marca."""
    nombre_marca = forms.CharField(
        label='Nombre de la marca',
        error_messages={'required': 'El nombre de la marca es obligatorio.'}
    )

    class Meta:
        model = Marcas
        fields = ['nombre_marca']
        widgets = {
            'nombre_marca': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la Marca'}),
        }
        labels = {
            'nombre_marca': 'Nombre de la Marca',
        }

    def clean_nombre_marca(self):
        nombre = self.cleaned_data.get('nombre_marca')
        nombre_limpio = nombre.strip().capitalize()

        instance_id = self.instance.pk

        queryset = Marcas.all_objects.filter(nombre_marca__iexact=nombre_limpio)
        if instance_id:
            queryset = queryset.exclude(pk=instance_id)

        if queryset.exists():
            raise ValidationError("Ya existe una marca con este nombre.")

        return nombre_limpio


# ===============================================
# FORMULARIO PROVEEDORES
# ===============================================

class ProveedorRegistroForm(forms.Form):
    cuit_prov = forms.CharField(
        max_length=15,
        required=True,
        label='CUIT',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 20-12345678-9'})
    )

    nombre_prov = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre/Razón Social',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    telefono_prov = forms.CharField(
        max_length=20,
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    email_prov = forms.EmailField(
        max_length=150,
        required=False,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    direccion_prov = forms.CharField(
        max_length=100,
        required=False,
        label='Dirección',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean_cuit_prov(self):
        cuit = self.cleaned_data.get('cuit_prov')
        if Proveedores.all_objects.filter(cuit_prov=cuit).exists():
            raise ValidationError("Ya existe un proveedor con este CUIT (activo o inactivo).")
        return cuit

    def clean_email_prov(self):
        email = self.cleaned_data.get('email_prov')
        if email and Proveedores.all_objects.filter(email_prov=email).exists():
            raise ValidationError("Ya existe un proveedor con este Email (activo o inactivo).")
        return email


# ===============================================
# FORMULARIO LOCALES COMERCIALES
# ===============================================

class LocalComercialRegistroForm(forms.Form):
    # La provincia se manejará como un ChoiceField para mostrar las provincias existentes
    id_provincia = forms.ModelChoiceField(
        queryset=Provincias.objects.all(),
        required=True,
        label='Provincia',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    nombre_loc_com = forms.CharField(
        max_length=100,
        required=True,
        label='Nombre del Local',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    cod_postal_loc_com = forms.IntegerField(
        required=False,
        label='Código Postal',
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    telefono_loc_com = forms.CharField(
        max_length=30,
        required=False,
        label='Teléfono',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    direccion_loc_com = forms.CharField(
        max_length=100,
        required=False,
        label='Dirección',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        id_provincia = cleaned_data.get('id_provincia')
        nombre_loc_com = cleaned_data.get('nombre_loc_com')

        # Validación del unique_together: (id_provincia, nombre_loc_com)
        if id_provincia and nombre_loc_com:
            if LocalesComerciales.all_objects.filter(
                id_provincia=id_provincia, 
                nombre_loc_com=nombre_loc_com
            ).exists():
                raise ValidationError(
                    "Ya existe un local comercial con este nombre en la provincia seleccionada (activo o inactivo)."
                )
        
        return cleaned_data


# ===============================================
# FORMULARIO PRODUCTOS
# ===============================================

class ProductoRegistroForm(forms.Form):
    nombre_producto = forms.CharField(
        max_length=150,
        required=True,
        label='Nombre del Producto',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    id_marca = forms.ModelChoiceField(
        queryset=Marcas.objects.all(),
        required=False,
        label='Marca',
        empty_label="-- Sin Marca --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    precio_unit_prod = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        label='Precio Unitario',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    
    fecha_venc_prod = forms.DateField(
        required=False,
        label='Fecha de Vencimiento',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    
    # NUEVOS CAMPOS
    tipo_unidad = forms.ChoiceField(
        choices=Productos.TIPO_UNIDAD_CHOICES,
        required=True,
        label='Tipo de Unidad',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    cantidad_por_pack = forms.IntegerField(
        required=False,
        label='Cantidad por Pack',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        help_text='Solo completar si el producto es un pack.'
    )

    def clean_nombre_producto(self):
        nombre = self.cleaned_data.get('nombre_producto')
        if Productos.all_objects.filter(nombre_producto__iexact=nombre).exists():
            raise ValidationError("Ya existe un producto con este nombre (activo o inactivo).")
        return nombre


class BilleteraRegistroForm(forms.Form):
    nombre_bv = forms.CharField(
        max_length=100,
        required=True,
        label='Nombre de la Billetera',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    usuario_bv = forms.CharField(
        max_length=100,
        required=True,
        label='Usuario (Alias/ID)',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    contrasena_bv = forms.CharField(
        max_length=255,
        required=True,
        label='Contraseña',
        # Usar PasswordInput para ocultar la entrada
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    cbu_bv = forms.CharField(
        max_length=22,
        required=False,
        label='CBU/CVU',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    saldo_bv = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        label='Saldo Inicial',
        initial=0.00,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )

    def clean_usuario_bv(self):
        usuario = self.cleaned_data.get('usuario_bv')
        if BilleterasVirtuales.all_objects.filter(usuario_bv__iexact=usuario).exists():
            raise ValidationError("Ya existe una billetera con este nombre de usuario (Alias/ID).")
        return usuario

    def clean_cbu_bv(self):
        cbu = self.cleaned_data.get('cbu_bv')
        if cbu and BilleterasVirtuales.all_objects.filter(cbu_bv=cbu).exists():
            raise ValidationError("Ya existe una billetera con este CBU/CVU.")
        return cbu
    
class BilleteraModificacionForm(forms.Form):
    # Campos que se pueden modificar
    nombre_bv = forms.CharField(max_length=100, required=True)
    usuario_bv = forms.CharField(max_length=100, required=True)
    cbu_bv = forms.CharField(max_length=22, required=False)
    saldo_bv = forms.DecimalField(max_digits=12, decimal_places=2, required=True)
    # La contraseña solo se modifica si se envía, de lo contrario se usa la vieja.
    nueva_contrasena_bv = forms.CharField(max_length=255, required=False)

    # Se omiten los métodos clean para permitir validación en la vista (excluyendo el objeto actual)