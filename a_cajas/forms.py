from django import forms
from .models import Cajas
# IMPORTANTE: Asumiendo que el modelo de Local Comercial se importa así:
# Si esta importación falla, usa el MOCKUP de models.py
try:
    from a_central.models import LocalesComerciales
except ImportError:
    # Usar el MOCKUP si la importación no funciona
    # Este es un MOCKUP para que el código compile si 'a_central' no está disponible.
    class LocalesComerciales:
        # Definición mínima requerida para el Select
        pass

class CajaForm(forms.ModelForm):
    # Campo auxiliar de solo lectura para mostrar el nombre del Local en el formulario de edición.
    local_readonly = forms.CharField(required=False, label='Local Comercial', 
                                     widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}))
    
    class Meta:
        model = Cajas
        # Se incluyen ambos campos. La lógica de ocultar/mostrar se maneja en __init__
        fields = ['id_loc_com', 'numero_caja']
        
        labels = {
            'id_loc_com': 'Local comercial', 
            'numero_caja': 'Número de caja',
        }
        
        widgets = {
             'numero_caja': forms.TextInput(attrs={'placeholder': 'Número de caja', 'class': 'form-control'}),
             # Añadimos la clase form-control al Select de locales
             'id_loc_com': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Añadir clase CSS por defecto a todos los campos (excepto los gestionados)
        for field_name, field in self.fields.items():
            if field_name not in ['id_loc_com', 'numero_caja', 'local_readonly']:
                 # Asegurar que el campo no sobrescriba widgets ya definidos (como Select o Hidden)
                field.widget.attrs.update({'class': 'form-control'})

        # Si se está modificando una instancia (edición):
        if self.instance.pk:
            
            # 1. Configuramos el campo 'local_readonly' con el nombre actual del local.
            self.fields['local_readonly'].initial = self.instance.id_loc_com.nombre_loc_com if self.instance.id_loc_com else 'No asignado'
            
            # 2. Hacemos que el campo original 'id_loc_com' sea un campo oculto (HiddenInput).
            # Esto permite que el valor se mantenga y se guarde al modificar, pero no se pueda cambiar.
            self.fields['id_loc_com'].widget = forms.HiddenInput()
            
            # 3. Ajustamos el orden de los campos: readonly, numero_caja, id_loc_com (oculto).
            new_order = ['local_readonly', 'numero_caja', 'id_loc_com']
            self.order_fields(new_order)
            
        # Si NO es edición (nuevo registro), eliminamos 'local_readonly'
        else:
            if 'local_readonly' in self.fields:
                del self.fields['local_readonly']
            # Aseguramos que el campo número y local tengan la clase correcta para registro
            self.fields['numero_caja'].widget.attrs['class'] = 'form-control'
            self.fields['id_loc_com'].widget.attrs['class'] = 'form-control'
