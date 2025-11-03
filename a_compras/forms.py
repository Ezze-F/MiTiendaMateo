from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from django.core.exceptions import ValidationError 
from a_central.models import Productos, Proveedores, LocalesComerciales, Marcas
from .models import Compras, DetallesCompras

class CompraForm(forms.ModelForm):
    proveedor = forms.ModelChoiceField(
        queryset=Proveedores.objects.filter(borrado_prov=False),
        label="Proveedor",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    local = forms.ModelChoiceField(
        queryset=LocalesComerciales.objects.filter(borrado_loc_com=False),
        label="Local Comercial",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Compras
        fields = []  # Los campos visibles los definimos manualmente arriba
        # Los campos automáticos se manejarán en la vista

class DetalleCompraForm(forms.ModelForm):
    class Meta:
        model = DetallesCompras
        fields = ['id_producto', 'cantidad']  # NO incluimos precio_unitario
        labels = {
            'id_producto': 'Producto',
            'cantidad': 'Cantidad',
            # 'marca': 'Marca',
        }
        widgets = {
            'id_producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            # 'marca': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtramos productos activos
        self.fields['id_producto'].queryset = Productos.objects.filter(borrado_prod=False)
        # # Filtramos marcas activas
        # self.fields['marca'].queryset = Marcas.objects.filter(borrado_marca=False)


# =========================================================
# CLASE BASE PARA VALIDAR UNICIDAD EN EL FORMSET
# =========================================================
class BaseDetalleCompraFormSet(forms.BaseInlineFormSet):
    """
    Formset base para DetalleCompras que valida la unicidad de productos
    dentro de la misma compra para prevenir IntegrityError por unique_together.
    """
    def clean(self):
        super().clean()
        if any(self.errors):
            # No ejecutar validación si ya hay errores de formulario
            return

        productos_ids = []
        for form in self.forms:
            # Solo considerar formularios que contienen datos y no están marcados para eliminación
            if form.cleaned_data and not form.cleaned_data.get('DELETE'):
                id_producto = form.cleaned_data.get('id_producto')
                
                # Verificamos si este producto ya fue agregado
                if id_producto in productos_ids:
                    # Lanzamos el error a nivel de formset
                    raise ValidationError(
                        'No puedes ingresar el mismo producto dos veces en la misma compra. Consolida la cantidad en una sola línea.',
                        code='duplicate_product'
                    )
                productos_ids.append(id_producto)


# Formset para múltiples productos en la misma compra
DetalleCompraFormSet = inlineformset_factory(
    Compras,
    DetallesCompras,
    form=DetalleCompraForm,
    formset=BaseDetalleCompraFormSet, # <--- Se aplica la validación de unicidad
    extra=1,
    can_delete=True
)

