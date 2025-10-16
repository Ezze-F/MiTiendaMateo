from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import IntegrityError
from django.contrib import messages
from django.db.models import Sum, Q, F # Importar Sum, Q y F para cálculos y anotaciones
from .models import Cajas, ArqueoCaja, PagosVentas, PagosCompras # Importar todos los modelos necesarios
from .forms import CajaForm

# ======================================================
# Funciones de Gestión de Estado (Abrir/Cerrar)
# ======================================================

@require_POST
def abrir_caja(request, caja_id):
    """Abre una caja y devuelve JSON si es AJAX."""
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    caja = get_object_or_404(Cajas, pk=caja_id)
    
    if caja.abrir():
        message = f"La Caja N°{caja.numero_caja} ha sido abierta."
        if is_ajax:
            return JsonResponse({'message': message}, status=200)
        else:
            messages.success(request, message)
    else:
        # Se obtiene el estado actual para un mensaje de error más claro
        estado_display = getattr(caja, 'get_estado_display', lambda: str(caja.estado))()
        error_message = f"No se pudo abrir la Caja N°{caja.numero_caja}. Estado actual: {estado_display}."
        if is_ajax:
            return JsonResponse({'error': error_message}, status=400)
        else:
            messages.error(request, error_message)
            
    return redirect('a_cajas:listar_cajas')

@require_POST
def cerrar_caja(request, caja_id):
    """Cierra una caja y devuelve JSON si es AJAX."""
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    caja = get_object_or_404(Cajas, pk=caja_id)
    
    if caja.cerrar():
        message = f"La Caja N°{caja.numero_caja} ha sido cerrada."
        if is_ajax:
            return JsonResponse({'message': message}, status=200)
        else:
            messages.success(request, message)
    else:
        estado_display = getattr(caja, 'get_estado_display', lambda: str(caja.estado))()
        error_message = f"No se pudo cerrar la Caja N°{caja.numero_caja}. Estado actual: {estado_display}."
        if is_ajax:
            return JsonResponse({'error': error_message}, status=400)
        else:
            messages.error(request, error_message)

    return redirect('a_cajas:listar_cajas')

# ======================================================
# Funciones CRUD y Listado Principal
# ======================================================

def listar_cajas(request):
    """Muestra todas las cajas activas."""
    cajas_activas = Cajas.objects.all().order_by('id_loc_com', 'numero_caja')
    form = CajaForm()
    
    context = {
        'cajas': cajas_activas,
        'form': form,
        'page_title': 'Gestión de Cajas Registradoras'
    }
    return render(request, 'a_cajas/listar_cajas.html', context)

def registrar_caja(request):
    """Crea una nueva caja y devuelve JSON si es AJAX."""
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        form = CajaForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                message = "Caja registrada exitosamente."
                if is_ajax:
                    return JsonResponse({'message': message}, status=201)
                else:
                    messages.success(request, message)
            except IntegrityError:
                error_message = "Error: Ya existe una caja con ese número en este local comercial."
                if is_ajax:
                    return JsonResponse({'error': error_message}, status=400)
                else:
                    messages.error(request, error_message)
        else:
            # Captura errores de formulario para AJAX
            errors = dict(form.errors.items())
            if is_ajax:
                return JsonResponse({'errors': errors, 'error': 'Errores de validación en el formulario.'}, status=400)
            else:
                messages.error(request, "Por favor, corrija los errores en el formulario.")
    
    return redirect('a_cajas:listar_cajas') 

def modificar_caja(request, caja_id):
    """Modifica una caja existente y devuelve JSON si es AJAX."""
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    caja = get_object_or_404(Cajas, pk=caja_id)
    
    if request.method == 'POST':
        form = CajaForm(request.POST, instance=caja)
        if form.is_valid():
            try:
                form.save()
                message = f"Caja N°{caja.numero_caja} modificada."
                if is_ajax:
                    return JsonResponse({'message': message}, status=200)
                else:
                    messages.success(request, message)
            except IntegrityError:
                error_message = "Error: Ya existe una caja con ese número en este local comercial."
                if is_ajax:
                    return JsonResponse({'error': error_message}, status=400)
                else:
                    messages.error(request, error_message)
        else:
            # Captura errores de formulario para AJAX
            errors = dict(form.errors.items())
            if is_ajax:
                return JsonResponse({'errors': errors, 'error': 'Errores de validación en el formulario.'}, status=400)
            else:
                messages.error(request, "Error al modificar: El formulario contiene errores.")
    
    return redirect('a_cajas:listar_cajas')


@require_POST
def borrar_caja(request, caja_id):
    """Borrado lógico de una caja (requiere que esté cerrada) y devuelve JSON si es AJAX."""
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    caja = get_object_or_404(Cajas, pk=caja_id)
    
    if caja.borrar_logico():
        message = f"Caja N°{caja.numero_caja} borrada lógicamente."
        if is_ajax:
            return JsonResponse({'message': message}, status=200)
        else:
            messages.warning(request, message)
    else:
        error_message = f"No se pudo borrar la Caja N°{caja.numero_caja}. Debe estar CERRADA primero."
        if is_ajax:
            return JsonResponse({'error': error_message}, status=400)
        else:
            messages.error(request, error_message)

    return redirect('a_cajas:listar_cajas')

@require_POST
def recuperar_caja(request, caja_id):
    """Recuperación de una caja borrada lógicamente, devuelve JSON si es AJAX."""
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    # Usa all_objects para encontrar cajas borradas
    caja = get_object_or_404(Cajas.all_objects, pk=caja_id) 
    
    if caja.restaurar():
        message = f"Caja N°{caja.numero_caja} recuperada."
        if is_ajax:
            # Éxito: Status 200 y mensaje
            return JsonResponse({'message': message}, status=200)
        else:
            messages.success(request, message)
    else:
        error_message = f"No se pudo recuperar la Caja N°{caja.numero_caja}."
        if is_ajax:
            # Error: Status 400 y mensaje de error
            return JsonResponse({'error': error_message}, status=400)
        else:
            messages.error(request, error_message)
            
    # Redireccionamos solo si no fue AJAX
    return redirect('a_cajas:listar_cajas')

# ======================================================
# Funciones API (Respuestas JSON)
# ======================================================


def cajas_disponibles_api(request):
    """Devuelve la lista de cajas activas (borrado_caja=False) en formato JSON para DataTables.
       Se modifica para devolver una lista de diccionarios, no una lista de listas,
       para que coincida con la configuración de DataTables en cajas.js.
    """
    
    # IMPORTANTE: El manager 'objects' en el modelo Cajas ya filtra por borrado_caja=False
    # Si quieres asegurar que estén solo las activas, usa el manager por defecto.
    cajas = Cajas.objects.all().select_related('id_loc_com') # Usar select_related para optimizar la consulta
    
    data = []
    for caja in cajas:
        local_nombre = caja.id_loc_com.nombre_loc_com if caja.id_loc_com else 'N/A'
        estado = 'Abierta' if caja.caja_abierta else 'Cerrada'
        
        # Estructura de datos para DataTables (lista de DICCIONARIOS)
        # Las claves deben coincidir con las definidas en "data" de cajas.js
        data.append({
            'id_caja': caja.id_caja,
            'id_loc_com': caja.id_loc_com.id_loc_com if caja.id_loc_com else None, # ID para el modal de modificar
            'id_loc_com__nombre_loc_com': local_nombre, # Nombre del local para la columna 1
            'numero_caja': caja.numero_caja,
            'caja_abierta': caja.caja_abierta, # Estado Booleano para el renderizado
            'estado_html': f'<span class="badge bg-{"success" if caja.caja_abierta else "danger"}">{estado}</span>', # Campo opcional si se quiere usar para display
            'acciones_html': f'''
                <button class="btn btn-sm btn-{"success" if not caja.caja_abierta else "danger"} action-btn" 
                        data-id="{caja.id_caja}" data-action="{"abrir" if not caja.caja_abierta else "cerrar"}">
                    {"Abrir" if not caja.caja_abierta else "Cerrar"}
                </button>
                <button class="btn btn-sm btn-warning action-btn" data-id="{caja.id_caja}" data-action="modificar">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger action-btn" data-id="{caja.id_caja}" data-action="eliminar">
                    <i class="fas fa-trash-alt"></i>
                </button>
            ''' # Este campo es redundante con el render JS, pero se puede dejar para debugging
        })
        
    return JsonResponse({'data': data})

def cajas_eliminadas_api(request):
    """API: Devuelve las cajas borradas lógicamente."""
    cajas = list(Cajas.all_objects.filter(borrado_caja=True).values(
        'id_caja', 'numero_caja', 'id_loc_com__nombre_loc_com', 'fh_borrado_caja'
    ).annotate(local=F('id_loc_com__nombre_loc_com')))
    
    data_list = []
    for caja in cajas:
        # Nota: La vista cajas_eliminadas_api ya retorna un JSON plano (no 'data': [...]),
        # lo cual es INCONSISTENTE con la forma de cajas_disponibles_api. 
        # Pero como cajas.js está configurado para manejar el JSON plano o con 'data' 
        # y ahora corregiremos cajas.js, no tocaremos esta función por ahora.
        
        caja['local'] = caja.pop('id_loc_com__nombre_loc_com')
        # Formatear la fecha
        if caja['fh_borrado_caja']:
            caja['fh_borrado_caja'] = caja['fh_borrado_caja'].strftime('%d-%m-%Y %H:%M')
        data_list.append(caja)
            
    return JsonResponse({'data': data_list}) # Envío ahora con {'data': ...} para unificar formato con cajas.js


def arqueos_api(request):
    """
    Retorna los datos de todos los ciclos de caja cerrados para DataTables.
    Realiza los cálculos de ingresos/egresos de BV y la diferencia de arqueo.
    """
    if request.method == 'GET':
        # 1. Obtener todos los arqueos CERRADOS
        # Solo necesitamos arqueos que tienen una fecha de cierre (fh_cierre IS NOT NULL)
        arqueos_cerrados = ArqueoCaja.objects.filter(fh_cierre__isnull=False).select_related('id_caja__id_loc_com').order_by('-fh_cierre')

        data = []
        for arqueo in arqueos_cerrados:
            
            # 2. Calcular Ingresos BV (Pagos de Ventas)
            ingresos_bv = PagosVentas.objects.filter(
                id_venta__fh_venta__range=(arqueo.fh_apertura, arqueo.fh_cierre),
                id_bv__isnull=False,
                borrado_pv=False
            ).aggregate(total=Sum('monto'))['total'] or 0.00
            
            # 3. Calcular Egresos BV (Pagos de Compras)
            egresos_bv = PagosCompras.objects.filter(
                id_compra__fh_compra__range=(arqueo.fh_apertura, arqueo.fh_cierre),
                id_bv__isnull=False,
                borrado_pc=False
            ).aggregate(total=Sum('monto'))['total'] or 0.00

            # Usamos los campos pre-calculados del modelo ArqueoCaja si existen:
            diferencia = arqueo.diferencia_arqueo if arqueo.diferencia_arqueo is not None else 0.00


            data.append({
                'id_arqueo': arqueo.id_arqueo,
                'local': str(arqueo.id_caja.id_loc_com), 
                'numero_caja': arqueo.id_caja.numero_caja,
                'fh_apertura': arqueo.fh_apertura.strftime('%d-%m-%Y %H:%M'),
                'fh_cierre': arqueo.fh_cierre.strftime('%d-%m-%Y %H:%M'),
                'monto_inicial_efectivo': float(arqueo.monto_inicial_efectivo),
                'monto_final_efectivo': float(arqueo.monto_final_efectivo) if arqueo.monto_final_efectivo is not None else 0.00,
                'total_ingresos_bv': float(ingresos_bv),
                'total_egresos_bv': float(egresos_bv),
                'diferencia_arqueo': float(diferencia),
                'estado_diferencia': 'Sobrante' if diferencia > 0 else ('Faltante' if diferencia < 0 else 'Cerrado OK')
            })
            
        return JsonResponse({'data': data}, safe=False)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
