import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from a_central.models import Marcas, Proveedores, LocalesComerciales, Productos
from django.views.decorators.csrf import csrf_exempt


def index(request):
    """
    Vista principal de la aplicación de stock.
    """
    # Ejemplo de uso de modelos: Obtener todas las marcas
    marcas = Marcas.objects.all() 
    context = {'marcas': marcas}
    
    # Aquí iría tu lógica de vista. Por ahora, solo devuelve una plantilla de ejemplo.
    return render(request, 'a_stock/index.html', context)