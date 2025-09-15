from django import forms
from .models import Roles

class RolesForm(forms.ModelForm):
    class Meta:
        model = Roles
        fields = ['nombre_rol', 'descripcion_rol']