from django.shortcuts import render, redirect, get_object_or_404
from a_productos.models import Productos
#from .forms import ProductForm
from django.http import JsonResponse # necesario para trabajar con AJAX

def listar_prod(request): # request quiere decir solicitado
    # Muestra la lista de productos totales, disponibles y eliminados.
    productos_totales = Productos.objects.all() # # el objeto productos_disponibles recibe todos los atributos que tiene la clase Productos del models.py de la app a_productos
    productos_disponibles = Productos.objects.filter(borrado_logico=True) # el objeto productos_disponibles recibe todos los atributos que tiene la clase Productos del models.py de la app a_productos excluyendo los eliminados lógicamente.
    productos_eliminados = Productos.objects.filter(borrado_logico=False) # el objeto productos_eliminados recibe todos los atributos que tiene la clase Productos del models.py de la app a_productos que fueron eliminados lógicamente.
    context = {
        'productos_totales': productos_totales,
        'listado_disponibles': productos_disponibles,
        'listado_eliminados': productos_eliminados,
    }
    return render(request, 'a_productos/listar_prod.html', context) # renderiza en la ruta 'productos/listar_productos.html' las dos pestañas que contiene context.

# def ingresar_prod(request):
#     # Registra un nuevo producto.
#     if (request.method == 'POST'): # se verifica la utilización del método POST para los datos enviados.
#         form = ProductForm(request.POST) # se guardan los datos enviados con el método POST en el objeto form
#         if form.is_valid(): # si los datos recibidos son válidos...
#             form.save() # se guardan los datos
#             return JsonResponse({'success': True}) # respuesta afirmativa
#         else:
#             return JsonResponse({'success': False, 'errors': form.errors}) # respuesta negativa
#     else: # no se utilizó el método POST (sino GET)
#         form = ProductForm() # el objeto form recibe el formulario ProductForm vacío
#         return render(request, 'a_productos/modal_ingresar_prod.html', {'form': form}) # 'form' es la variable donde se cargarán los datos del formulario (debe coincidir en el html).

# def editar_prod(request, pk): # pk será el valor a buscar para la modificación del registro
#     # Funcionalidad con AJAX. Modifica un producto existente, incluyendo eliminados.
#     producto = get_object_or_404(Productos.all_objects, pk=pk) # si no se encuentra el producto, se lanza una página con el error 404
#     if (request.method == 'POST'): # se verifica la utilización del método POST para los datos enviados
#         form = ProductForm(request.POST, instance=producto) # si se usa POST, se guarda en la variable instance lo que contenga producto para modificar sus valores
#         if form.is_valid(): # si los datos recibidos son válidos...
#             form.save() # se guardan los datos
#             return JsonResponse({'success': True}) # respuesta afirmativa
#         else:
#             return JsonResponse({'success': False, 'errors': form.errors}) # respuesta negativa
#     else: # no se utilizó el método POST (sino GET)
#         form = ProductForm(instance=producto) # se carga el formulario con los datos encontrados
#         template = 'a_productos/modal_editar_prod.html' if request.headers.get('x-requested-with') == 'XMLHttpRequest' else 'a_productos/editar_producto.html'
#         return render(request, template, {'form': form})

# def eliminar_prod(request, pk): # pk será el valor a buscar para la eliminación del registro
#     # Elimina lógicamente un producto.
#     producto = get_object_or_404(Productos.all_objects, pk=pk) # si no se encuentra el producto, se lanza una página con el error 404
#     if (request.method == 'POST'): # se verifica la utilización del método POST para los datos enviados
#         producto.soft_delete() # se utiliza el método sof_delete() para borrar lógicamente el registro
#         return JsonResponse({'success': True}) # redirecciona al listar_productos.html (Aquí se podría mostrar un mensaje de eliminación correcta)
#     return render(request, 'a_productos/eliminar_producto_modal.html', {'producto': producto})

# def restaurar_prod(request, pk): # pk será el valor a buscar para la eliminación del registro
#     # Restaura un producto eliminado lógicamente.
#     producto = get_object_or_404(Productos.all_objects, pk=pk) # si no se encuentra el producto, se lanza una página con el error 404
#     if request.method == 'POST': # se verifica la utilización del método POST para los datos enviados
#         producto.restore() # se utiliza el método restore() para restaurar el registro borrado lógicamente-
#         return JsonResponse({'success': True})
#     return render(request, 'productos/restaurar_producto_modal.html', {'producto': producto})
