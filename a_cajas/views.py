from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET 
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.db.models import Sum, Q, F 
from django.utils import timezone 
from decimal import Decimal, InvalidOperation 
from .models import Cajas, ArqueoCaja, PagosVentas, PagosCompras, MovimientosFinancieros
from a_compras.models import Compras
from .forms import CajaForm
from a_ventas.models import Ventas
import logging

logger = logging.getLogger(__name__)

# IMPORTACIONES ASUMIDAS (Asegúrate que estas importaciones sean correctas en tu proyecto)
try:
    # Si Empleados está en 'a_central', ajústalo
    from a_central.models import Empleados 
except ImportError:
    class Empleados: 
        """Clase mockup para evitar errores si no se encuentra Empleados."""
        objects = None 
        pass 

# ======================================================
# Funciones de Gestión de Estado (Abrir/Cerrar)
# ======================================================

@require_POST
def abrir_caja(request, caja_id):
    """
    Abre una caja, CREA el registro ArqueoCaja con el monto inicial y el empleado
    de apertura, y devuelve JSON si es AJAX.
    """
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    try:
        caja = get_object_or_404(Cajas, pk=caja_id)
        
        # 1. Validar estado de la caja
        if caja.caja_abierta:
            raise ValueError("La caja ya se encuentra abierta.")
        
        # 2. Obtener y validar Monto Inicial
        monto_str = request.POST.get('efectivo_inicial', '0')
        if not monto_str:
            raise ValueError("El monto inicial de efectivo es requerido.")
            
        try:
            # Reemplazar comas por puntos si se usan como separador decimal y forzar Decimal
            monto_inicial = Decimal(monto_str.replace(',', '.')) 
        except InvalidOperation:
            raise ValueError("Formato de monto inicial inválido.")
            
        if monto_inicial < 0:
            raise ValueError("El monto inicial no puede ser negativo.")

        # 3. Obtener el Empleado de Apertura (ASUMIDO: Se obtiene del usuario logueado)
        if not request.user.is_authenticated:
            raise ValueError("Usuario no autenticado para abrir caja.")
            
        # --- LÓGICA CLAVE: Obtener el objeto Empleados ---
        try:
            empleado_apertura = Empleados.objects.get(user_auth=request.user) 
        except Empleados.DoesNotExist:
             raise ValueError("No se encontró un empleado asociado al usuario de autenticación.")
        # ------------------------------------------------

        # 4. Ejecutar la transacción de apertura y creación del arqueo
        with transaction.atomic():
            # A. Abrir la caja (solo cambia el estado en el modelo Cajas)
            if not caja.abrir(): 
                 # Si el método abrir falla (e.g., ya está abierta, aunque ya validamos)
                 raise Exception("Fallo al cambiar el estado de la caja.")

            # B. CREAR EL REGISTRO DE ARQUEOCAJAS
            ArqueoCaja.objects.create(
                id_caja=caja,
                fh_apertura=timezone.now(),
                monto_inicial_efectivo=monto_inicial,
                id_empleado_apertura=empleado_apertura,
                # Otros campos quedan en NULL/Default (fh_cierre, monto_final, etc.)
            )

        message = f"La Caja N°{caja.numero_caja} ha sido abierta e iniciado un nuevo ciclo de arqueo con ${monto_inicial:.2f}."
        
        if is_ajax:
            return JsonResponse({'message': message}, status=200)
        else:
            messages.success(request, message)

    except (ValueError, IntegrityError) as ve:
        error_message = str(ve)
        if is_ajax:
            return JsonResponse({'error': error_message}, status=400)
        else:
            messages.error(request, error_message)
    except Exception as e:
        error_message = f"Error inesperado al abrir la caja: {str(e)}"
        if is_ajax:
            return JsonResponse({'error': error_message}, status=500)
        else:
            messages.error(request, error_message)
            
    return redirect('a_cajas:listar_cajas')


@require_POST
def cerrar_caja(request, caja_id):
    """
    Función de cierre simple (solo cambio de estado sin arqueo).
    """
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    caja = get_object_or_404(Cajas, pk=caja_id)
    
    try:
        # Si la caja tiene un arqueo abierto, no permitir cierre simple
        if ArqueoCaja.objects.filter(id_caja=caja, fh_cierre__isnull=True).exists():
            error_message = f"La Caja N°{caja.numero_caja} tiene un arqueo pendiente. Use 'Realizar Arqueo' para el cierre completo."
            if is_ajax:
                return JsonResponse({'error': error_message}, status=400)
            else:
                messages.warning(request, error_message)
                return redirect('a_cajas:listar_cajas')

        # Cerrar la caja si no hay arqueo activo
        if caja.cerrar():
            message = f"La Caja N°{caja.numero_caja} ha sido cerrada (sin arqueo)."
            if is_ajax:
                return JsonResponse({'message': message}, status=200)
            else:
                messages.success(request, message)
        else:
            error_message = f"No se pudo cerrar la Caja N°{caja.numero_caja}."
            if is_ajax:
                return JsonResponse({'error': error_message}, status=400)
            else:
                messages.error(request, error_message)

    except Exception as e:
        error_message = f"Error al cerrar la caja: {str(e)}"
        if is_ajax:
            return JsonResponse({'error': error_message}, status=500)
        else:
            messages.error(request, error_message)

    return redirect('a_cajas:listar_cajas')

# ======================================================
# Funciones CRUD y Listado Principal (SIN CAMBIOS)
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

@require_GET
def datos_arqueo_actual_api(request, caja_id):
    """
    Retorna los datos de transacciones del ciclo de caja actualmente ABIERTO
    para una caja específica, calculando automáticamente ingresos y egresos.
    SEPARADO POR EFECTIVO Y BILLETERA VIRTUAL.
    """
    try:
        # 1. Obtener la caja
        caja = get_object_or_404(Cajas, pk=caja_id)

        # 2. Obtener el último arqueo abierto (el ciclo activo)
        arqueo_activo = ArqueoCaja.objects.filter(
            id_caja=caja, 
            fh_cierre__isnull=True
        ).order_by('-fh_apertura').first()

        if not arqueo_activo:
            return JsonResponse({'error': f'La Caja N°{caja.numero_caja} no tiene un ciclo de arqueo activo (abierto).'}, status=404)
        
        # El rango de tiempo es desde la apertura hasta el momento actual
        apertura = arqueo_activo.fh_apertura
        ahora = timezone.now()
        
        # 3. Calcular INGRESOS en EFECTIVO (Ventas realizadas en esta caja durante el ciclo con medio_pago='EFECTIVO')
        ingresos_efectivo = Decimal('0.00')
        ingresos_bv = Decimal('0.00')
        
        # Obtener ventas del ciclo
        ventas_ciclo = Ventas.objects.filter(
            id_caja=caja,
            fh_venta__range=(apertura, ahora),
            borrado_venta=False
        )
        
        # Contadores para estadísticas
        ventas_efectivo_count = 0
        ventas_bv_count = 0
        
        for venta in ventas_ciclo:
            # Determinar el tipo de venta basado en movimientos financieros
            movimiento = MovimientosFinancieros.objects.filter(
                concepto__contains=f'Venta #{venta.id_venta}'
            ).first()
            
            if movimiento:
                if movimiento.medio_pago == 'EFECTIVO':
                    ingresos_efectivo += venta.total_venta
                    ventas_efectivo_count += 1
                elif movimiento.medio_pago == 'BILLETERA_VIRTUAL':
                    ingresos_bv += venta.total_venta
                    ventas_bv_count += 1

        # 4. Calcular EGRESOS en EFECTIVO (Compras pagadas en efectivo durante el ciclo)
        egresos_efectivo = Decimal('0.00')
        egresos_bv = Decimal('0.00')
        
        # Buscar compras pagadas durante este ciclo
        compras_ciclo = Compras.objects.filter(
            fecha_hora_compra__range=(apertura, ahora),
            situacion_compra="Completada"
        )
        
        compras_efectivo_count = 0
        compras_bv_count = 0
        
        for compra in compras_ciclo:
            # Verificar movimientos financieros de esta compra
            movimientos_compra = MovimientosFinancieros.objects.filter(
                id_compra=compra,
                fh_movimiento__range=(apertura, ahora)
            )
            
            for movimiento in movimientos_compra:
                if movimiento.tipo_movimiento == 'EGRESO':
                    if movimiento.medio_pago == 'EFECTIVO':
                        egresos_efectivo += movimiento.monto
                        compras_efectivo_count += 1
                    elif movimiento.medio_pago == 'BILLETERA_VIRTUAL':
                        egresos_bv += movimiento.monto
                        compras_bv_count += 1

        # 5. Calcular Saldo Esperado (solo en efectivo)
        monto_inicial = arqueo_activo.monto_inicial_efectivo
        saldo_esperado_efectivo = monto_inicial + ingresos_efectivo - egresos_efectivo

        data = {
            'id_arqueo': arqueo_activo.id_arqueo,
            'caja_id': caja.id_caja,
            'numero_caja': caja.numero_caja,
            'local': str(caja.id_loc_com),
            'fh_apertura': apertura.strftime('%Y-%m-%d %H:%M:%S'),
            'monto_inicial_efectivo': float(monto_inicial),
            
            # EFECTIVO
            'total_ingresos_efectivo': float(ingresos_efectivo),
            'total_egresos_efectivo': float(egresos_efectivo),
            'saldo_esperado_efectivo': float(saldo_esperado_efectivo),
            'ventas_efectivo_count': ventas_efectivo_count,
            'compras_efectivo_count': compras_efectivo_count,
            
            # BILLETERA VIRTUAL
            'total_ingresos_bv': float(ingresos_bv),
            'total_egresos_bv': float(egresos_bv),
            'ventas_bv_count': ventas_bv_count,
            'compras_bv_count': compras_bv_count,
            
            # TOTALES
            'ventas_total_count': ventas_efectivo_count + ventas_bv_count,
            'compras_total_count': compras_efectivo_count + compras_bv_count,
        }
            
        return JsonResponse(data)

    except Exception as e:
        logger.error(f"Error en datos_arqueo_actual_api: {str(e)}")
        return JsonResponse({'error': f"Error al obtener datos del arqueo actual: {str(e)}"}, status=500)


@require_POST
def registrar_cierre_arqueo(request, caja_id):
    """
    Registra el cierre automático de caja calculando ingresos y egresos reales
    SEPARADOS POR EFECTIVO Y BILLETERA VIRTUAL.
    """
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    caja = get_object_or_404(Cajas, pk=caja_id)
    
    try:
        # 1. Validar que la caja esté abierta
        if not caja.caja_abierta:
            raise ValueError(f"La Caja N°{caja.numero_caja} ya está cerrada.")

        # 2. Encontrar el arqueo activo
        arqueo_activo = ArqueoCaja.objects.filter(
            id_caja=caja, 
            fh_cierre__isnull=True
        ).order_by('-fh_apertura').first()
        
        if not arqueo_activo:
            raise Exception(f"Error interno: No se encontró un ciclo de arqueo activo para la Caja N°{caja.numero_caja}.")

        # 3. Recalcular movimientos automáticamente (SEPARADOS)
        apertura = arqueo_activo.fh_apertura
        ahora = timezone.now()
        
        # CALCULAR INGRESOS REALES (SEPARADOS POR TIPO DE PAGO)
        ingresos_efectivo = Decimal('0.00')
        ingresos_bv = Decimal('0.00')
        
        ventas_ciclo = Ventas.objects.filter(
            id_caja=caja,
            fh_venta__range=(apertura, ahora),
            borrado_venta=False
        )
        
        ventas_efectivo_count = 0
        ventas_bv_count = 0
        
        for venta in ventas_ciclo:
            # Determinar tipo de venta basado en movimientos financieros
            movimiento = MovimientosFinancieros.objects.filter(
                concepto__contains=f'Venta #{venta.id_venta}'
            ).first()
            
            if movimiento:
                if movimiento.medio_pago == 'EFECTIVO':
                    ingresos_efectivo += venta.total_venta
                    ventas_efectivo_count += 1
                elif movimiento.medio_pago == 'BILLETERA_VIRTUAL':
                    ingresos_bv += venta.total_venta
                    ventas_bv_count += 1

        # CALCULAR EGRESOS REALES (SEPARADOS POR TIPO DE PAGO)
        egresos_efectivo = Decimal('0.00')
        egresos_bv = Decimal('0.00')
        
        compras_ciclo = Compras.objects.filter(
            fecha_hora_compra__range=(apertura, ahora),
            situacion_compra="Completada"
        )
        
        compras_efectivo_count = 0
        compras_bv_count = 0
        
        for compra in compras_ciclo:
            movimientos_compra = MovimientosFinancieros.objects.filter(
                id_compra=compra,
                fh_movimiento__range=(apertura, ahora)
            )
            
            for movimiento in movimientos_compra:
                if movimiento.tipo_movimiento == 'EGRESO':
                    if movimiento.medio_pago == 'EFECTIVO':
                        egresos_efectivo += movimiento.monto
                        compras_efectivo_count += 1
                    elif movimiento.medio_pago == 'BILLETERA_VIRTUAL':
                        egresos_bv += movimiento.monto
                        compras_bv_count += 1

        # 4. Calcular monto final esperado automáticamente (SOLO EFECTIVO)
        monto_inicial = arqueo_activo.monto_inicial_efectivo
        saldo_esperado_efectivo = monto_inicial + ingresos_efectivo - egresos_efectivo
        
        # 5. Obtener el monto físico contado (esto sí lo ingresa el usuario)
        monto_final_str = request.POST.get('monto_final_efectivo')
        if not monto_final_str:
            raise ValueError("El monto final de efectivo (conteo físico) es requerido.")
            
        try:
            monto_final_efectivo = Decimal(monto_final_str.replace(',', '.'))
        except InvalidOperation:
            raise ValueError("Formato de monto final inválido.")

        # 6. Calcular diferencia (físico vs sistema) - SOLO EFECTIVO
        diferencia = monto_final_efectivo - saldo_esperado_efectivo
        
        # 7. Guardar el Arqueo y cerrar la Caja
        with transaction.atomic():
            arqueo_activo.monto_final_efectivo = monto_final_efectivo
            
            # Guardar los totales calculados automáticamente (SEPARADOS)
            arqueo_activo.total_ingresos_efectivo_calculado = ingresos_efectivo 
            arqueo_activo.total_egresos_efectivo_calculado = egresos_efectivo 
            
            # Totales de billeteras virtuales (calculados automáticamente)
            arqueo_activo.total_ingresos_bv = ingresos_bv
            arqueo_activo.total_egresos_bv = egresos_bv
            
            arqueo_activo.diferencia_arqueo = diferencia
            arqueo_activo.fh_cierre = ahora 
            arqueo_activo.cerrado = True 
            
            # Obtener empleado de cierre
            try:
                empleado_cierre = Empleados.objects.get(user_auth=request.user)
                arqueo_activo.id_empleado_cierre = empleado_cierre
            except Empleados.DoesNotExist:
                raise ValueError("Error de autenticación: No se encontró un empleado asociado al usuario.")

            arqueo_activo.save()
            
            # Cerrar la caja
            caja.cerrar()
        
        # 8. Responder al usuario con resumen completo
        estado_diferencia = 'Sobrante' if diferencia > 0 else ('Faltante' if diferencia < 0 else 'Perfecto')
        
        message = f"""
        Cierre de Caja N°{caja.numero_caja} registrado exitosamente.
        
        RESUMEN EFECTIVO:
        • Efectivo inicial: ${monto_inicial:.2f}
        • Ingresos por ventas: ${ingresos_efectivo:.2f} ({ventas_efectivo_count} ventas)
        • Egresos por compras: ${egresos_efectivo:.2f} ({compras_efectivo_count} compras)
        • Saldo esperado: ${saldo_esperado_efectivo:.2f}
        • Efectivo físico: ${monto_final_efectivo:.2f}
        • Diferencia: ${abs(diferencia):.2f} ({estado_diferencia})
        
        RESUMEN BILLETERAS VIRTUALES:
        • Ingresos por ventas BV: ${ingresos_bv:.2f} ({ventas_bv_count} ventas)
        • Egresos por compras BV: ${egresos_bv:.2f} ({compras_bv_count} compras)
        • Saldo neto BV: ${(ingresos_bv - egresos_bv):.2f}
        
        TOTALES DEL CICLO:
        • Ventas totales: {ventas_efectivo_count + ventas_bv_count} transacciones
        • Compras totales: {compras_efectivo_count + compras_bv_count} transacciones
        • Movimiento total: ${(ingresos_efectivo + ingresos_bv - egresos_efectivo - egresos_bv):.2f}
        """
        
        if is_ajax:
            return JsonResponse({
                'message': message, 
                'diferencia': float(diferencia),
                'estado_diferencia': estado_diferencia,
                'resumen': {
                    'efectivo_inicial': float(monto_inicial),
                    'ingresos_efectivo': float(ingresos_efectivo),
                    'egresos_efectivo': float(egresos_efectivo),
                    'saldo_esperado_efectivo': float(saldo_esperado_efectivo),
                    'efectivo_fisico': float(monto_final_efectivo),
                    'ingresos_bv': float(ingresos_bv),
                    'egresos_bv': float(egresos_bv),
                    'ventas_efectivo_count': ventas_efectivo_count,
                    'ventas_bv_count': ventas_bv_count,
                    'compras_efectivo_count': compras_efectivo_count,
                    'compras_bv_count': compras_bv_count
                }
            }, status=200)
        else:
            if diferencia != 0:
                messages.warning(request, message)
            else:
                messages.success(request, message)

    except ValueError as ve:
        error_message = str(ve)
        if is_ajax:
            return JsonResponse({'error': error_message}, status=400)
        messages.error(request, error_message)
    except Exception as e:
        error_message = f"Error inesperado al registrar el arqueo: {str(e)}"
        if is_ajax:
            return JsonResponse({'error': error_message}, status=500)
        messages.error(request, error_message)

    return redirect('a_cajas:listar_cajas')

def cajas_disponibles_api(request):
    """Devuelve la lista de cajas activas (borrado_caja=False) en formato JSON para DataTables.
       Se modifica para devolver una lista de diccionarios, no una lista de listas,
       para que coincida con la configuración de DataTables en cajas.js.
    """
    
    # IMPORTANTE: El manager 'objects' en el modelo Cajas ya filtra por borrado_caja=False
    # Si quieres asegurar que estén solo las activas, usa el manager por defecto.
    cajas = Cajas.objects.all().select_related('id_loc_com') # Usar select_related para optimizar la consulta
    
    data = []
    # Obtener IDs de cajas con arqueo abierto para mejorar rendimiento del loop
    arqueos_abiertos_ids = ArqueoCaja.objects.filter(fh_cierre__isnull=True).values_list('id_caja_id', flat=True)
    
    for caja in cajas:
        local_nombre = caja.id_loc_com.nombre_loc_com if caja.id_loc_com else 'N/A'
        estado = 'Abierta' if caja.caja_abierta else 'Cerrada'
        
        # Determinar si hay un arqueo activo (importante para habilitar el botón de cierre/arqueo)
        tiene_arqueo_activo = caja.id_caja in arqueos_abiertos_ids
        
        # Estructura de datos para DataTables (lista de DICCIONARIOS)
        # Las claves deben coincidir con las definidas en "data" de cajas.js
        data.append({
            'id_caja': caja.id_caja,
            'id_loc_com': caja.id_loc_com.id_loc_com if caja.id_loc_com else None, # ID para el modal de modificar
            'id_loc_com__nombre_loc_com': local_nombre, # Nombre del local para la columna 1
            'numero_caja': caja.numero_caja,
            'caja_abierta': caja.caja_abierta, # Estado Booleano para el renderizado
            'estado_html': f'<span class="badge bg-{"success" if caja.caja_abierta else "danger"}">{estado}</span>', # Campo opcional si se quiere usar para display
            'tiene_arqueo_activo': tiene_arqueo_activo, # Nuevo campo para JS
            'acciones_html': f'''
                <button class="btn btn-sm btn-{"success" if not caja.caja_abierta else ("info" if tiene_arqueo_activo else "danger")} action-btn" 
                        data-id="{caja.id_caja}" data-action="{"abrir" if not caja.caja_abierta else ("arqueo" if tiene_arqueo_activo else "cerrar")}"
                        title="{"Abrir Caja" if not caja.caja_abierta else ("Realizar Arqueo" if tiene_arqueo_activo else "Cerrar Caja (sin arqueo)")}">
                    {"Abrir" if not caja.caja_abierta else ("Arqueo" if tiene_arqueo_activo else "Cerrar")}
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
        caja['local'] = caja.pop('id_loc_com__nombre_loc_com')
        # Formatear la fecha
        if caja['fh_borrado_caja']:
            # Usar formato estándar para que el frontend lo pueda parsear
            caja['fh_borrado_caja'] = caja['fh_borrado_caja'].strftime('%Y-%m-%d %H:%M:%S')
        data_list.append(caja)
            
    return JsonResponse({'data': data_list}) # Envío ahora con {'data': ...} para unificar formato con cajas.js


def arqueos_api(request):
    """
    Retorna los datos de todos los ciclos de caja (ABIERTOS y CERRADOS) para DataTables.
    **MODIFICACIÓN:** Ahora incluye 'efectivo_ingresos' y 'efectivo_egresos' 
    que fueron guardados al momento del cierre.
    """
    if request.method == 'GET':
        arqueos = ArqueoCaja.objects.all().select_related(
            'id_caja', 
            'id_caja__id_loc_com',
            'id_empleado_apertura', 
            'id_empleado_cierre'    
        ).order_by('-fh_apertura') 
        
        data = []
        for arqueo in arqueos:
            
            es_cerrado = arqueo.fh_cierre is not None
            
            # Inicializar los campos de movimiento y diferencia
            ingresos_efectivo = Decimal('0.00')
            egresos_efectivo = Decimal('0.00')
            ingresos_bv = Decimal('0.00')
            egresos_bv = Decimal('0.00')
            diferencia = Decimal('0.00')
            
            if es_cerrado:
                # Recuperar los valores guardados al momento del cierre
                ingresos_efectivo = arqueo.total_ingresos_efectivo_calculado if arqueo.total_ingresos_efectivo_calculado is not None else Decimal('0.00')
                egresos_efectivo = arqueo.total_egresos_efectivo_calculado if arqueo.total_egresos_efectivo_calculado is not None else Decimal('0.00')
                ingresos_bv = arqueo.total_ingresos_bv if arqueo.total_ingresos_bv is not None else Decimal('0.00')
                egresos_bv = arqueo.total_egresos_bv if arqueo.total_egresos_bv is not None else Decimal('0.00')
                diferencia = arqueo.diferencia_arqueo if arqueo.diferencia_arqueo is not None else Decimal('0.00')

            
            local_nombre = str(arqueo.id_caja.id_loc_com) if arqueo.id_caja and arqueo.id_caja.id_loc_com else 'N/A'
            numero_caja = arqueo.id_caja.numero_caja if arqueo.id_caja else 'N/A'
            
            # --- CLAVES DE EMPLEADOS AJUSTADAS PARA MATCH CON CAJAS.JS ---
            empleado_apertura_nombre = str(arqueo.id_empleado_apertura) if arqueo.id_empleado_apertura else 'N/A'
            empleado_cierre_nombre = str(arqueo.id_empleado_cierre) if arqueo.id_empleado_cierre and es_cerrado else '' # Enviar string vacío si no se ha cerrado
            
            # --- FORMATO DE FECHA ESTANDARIZADO A YYYY-MM-DD HH:MM:SS ---
            # Esto es crucial para que new Date(str) funcione en el frontend sin errores de zona horaria/formato
            fh_cierre_str = arqueo.fh_cierre.strftime('%Y-%m-%d %H:%M:%S') if es_cerrado else None 
            fh_apertura_str = arqueo.fh_apertura.strftime('%Y-%m-%d %H:%M:%S')
            # -------------------------------------------------------------

            data.append({
                'id': arqueo.id_arqueo, # Clave 'id' usada en cajas.js
                'local_nombre': local_nombre, # Clave 'local_nombre' usada en cajas.js
                'caja_numero': numero_caja,
                
                'fecha_hora_apertura': fh_apertura_str, 
                'fecha_hora_cierre': fh_cierre_str,
                
                # Coincidir con las claves de 'data' en cajas.js (Columna 4 y 6)
                'empleado_apertura_nombre': empleado_apertura_nombre,
                'empleado_cierre_nombre': empleado_cierre_nombre, 

                # Coincidir con las claves de 'data' en cajas.js (Columna 7, 8, 9, 10, 11)
                'efectivo_inicial': float(arqueo.monto_inicial_efectivo),
                'efectivo_final': float(arqueo.monto_final_efectivo) if es_cerrado and arqueo.monto_final_efectivo is not None else None,
                # NUEVOS CAMPOS AÑADIDOS
                'efectivo_ingresos': float(ingresos_efectivo),
                'efectivo_egresos': float(egresos_efectivo),
                
                'ingresos_bv': float(ingresos_bv),
                'egresos_bv': float(egresos_bv),
                'diferencia': float(diferencia),
                
            })

        # Para el modo cliente, simplemente devolvemos los datos en el formato correcto:
        return JsonResponse({'data': data}, safe=False)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)
