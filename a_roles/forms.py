from django import forms
from .models import Roles

class RolForm(forms.ModelForm):
    class Meta:
        model = Roles
        fields = ['nombre_rol', 'descripcion_rol']
        widgets = {
            'nombre_rol': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_rol': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
