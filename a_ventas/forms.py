from django import forms
from .models import Ventas, DetallesVentas
from a_stock.models import Stock

class VentaForm(forms.ModelForm):
    class Meta:
        model = Ventas
        fields = ['id_loc_com', 'id_caja', 'id_empleado']
        widgets = {
            'id_loc_com': forms.Select(attrs={'class': 'form-control', 'id': 'id_loc_com'}),
            'id_caja': forms.Select(attrs={'class': 'form-control', 'id': 'id_caja'}),
            'id_empleado': forms.Select(attrs={'class': 'form-control', 'id': 'id_empleado'}),
        }

class DetalleVentaForm(forms.ModelForm):
    codigo_producto = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Código o nombre del producto',
            'id': 'buscar_producto'
        })
    )
    
    class Meta:
        model = DetallesVentas
        fields = ['id_producto', 'cantidad', 'precio_unitario_venta']
        widgets = {
            'id_producto': forms.HiddenInput(),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'value': 1
            }),
            'precio_unitario_venta': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'readonly': 'readonly'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        id_producto = cleaned_data.get('id_producto')
        cantidad = cleaned_data.get('cantidad')
        id_loc_com = self.data.get('id_loc_com')  # Obtenemos el local comercial del formulario principal

        if id_producto and cantidad and id_loc_com:
            # Verificar stock disponible
            try:
                stock = Stock.objects.get(
                    id_producto=id_producto, 
                    id_loc_com_id=id_loc_com,
                    borrado_pxlc=False
                )
                if stock.stock_pxlc < cantidad:
                    raise forms.ValidationError(
                        f"Stock insuficiente. Solo hay {stock.stock_pxlc} unidades disponibles."
                    )
            except Stock.DoesNotExist:
                raise forms.ValidationError("Producto sin stock en este local comercial.")

        return cleaned_data