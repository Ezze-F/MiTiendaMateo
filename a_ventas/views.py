from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, date
from decimal import Decimal

from .models import Ventas, DetallesVentas
from .forms import VentaForm, DetalleVentaForm
from a_central.models import Productos, Empleados, LocalesComerciales
from a_stock.models import Stock
from a_cajas.models import Cajas, PagosVentas, MovimientosFinancieros, ArqueoCaja

def listar_ventas(request):
    """Lista todas las ventas realizadas"""
    ventas = Ventas.objects.filter(borrado_venta=False).select_related(
        'id_loc_com', 'id_empleado', 'id_caja'
    ).order_by('-fh_venta')
    
    context = {
        'ventas': ventas,
        'page_title': 'Historial de Ventas'
    }
    return render(request, 'a_ventas/listar_ventas.html', context)

def registrar_venta(request):
    """Registra una nueva venta con sus detalles"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Crear la venta
                venta = Ventas(
                    id_loc_com_id=request.POST.get('id_loc_com'),
                    id_caja_id=request.POST.get('id_caja'),
                    id_empleado_id=request.POST.get('id_empleado'),
                    fh_venta=timezone.now(),
                    total_venta=0
                )
                venta.save()
                
                # Procesar detalles de venta
                detalles_data = request.POST.getlist('detalles')
                total_venta = Decimal('0.00')
                
                for detalle_str in detalles_data:
                    if detalle_str:
                        producto_id, cantidad, precio = detalle_str.split('|')
                        
                        # Crear detalle de venta
                        detalle = DetallesVentas(
                            id_venta=venta,
                            id_producto_id=int(producto_id),
                            cantidad=int(cantidad),
                            precio_unitario_venta=Decimal(precio),
                            subtotal=int(cantidad) * Decimal(precio)
                        )
                        detalle.save()
                        
                        # Actualizar stock
                        stock = Stock.objects.get(
                            id_producto_id=int(producto_id),
                            id_loc_com=venta.id_loc_com,
                            borrado_pxlc=False
                        )
                        stock.stock_pxlc -= int(cantidad)
                        stock.save()
                        
                        total_venta += detalle.subtotal
                
                # Actualizar total de la venta
                venta.total_venta = total_venta
                venta.save()
                
                # Registrar pago (asumiendo pago en efectivo por defecto)
                if venta.id_caja:
                    # Buscar arqueo de caja activo
                    arqueo_activo = ArqueoCaja.objects.filter(
                        id_caja=venta.id_caja,
                        fh_cierre__isnull=True
                    ).first()
                    
                    if arqueo_activo:
                        # Registrar movimiento financiero
                        MovimientosFinancieros.objects.create(
                            id_arqueo=arqueo_activo,
                            medio_pago='EFECTIVO',
                            tipo_movimiento='INGRESO',
                            concepto=f'Venta #{venta.id_venta}',
                            monto=total_venta,
                            fh_movimiento=timezone.now()
                        )
                
                messages.success(request, f'Venta registrada exitosamente. Total: ${total_venta:.2f}')
                return redirect('a_ventas:detalle_venta', venta_id=venta.id_venta)
                
        except Exception as e:
            messages.error(request, f'Error al registrar la venta: {str(e)}')
    
    # GET request - mostrar formulario vacío
    form = VentaForm()
    detalle_form = DetalleVentaForm()
    locales = LocalesComerciales.objects.filter(borrado_loc_com=False)
    empleados = Empleados.objects.filter(borrado_emp=False)
    
    context = {
        'form': form,
        'detalle_form': detalle_form,
        'locales': locales,
        'empleados': empleados,
        'page_title': 'Registrar Nueva Venta'
    }
    return render(request, 'a_ventas/registrar_venta.html', context)

def detalle_venta(request, venta_id):
    """Muestra el detalle de una venta específica"""
    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetallesVentas.objects.filter(
        id_venta=venta, 
        borrado_det_v=False
    ).select_related('id_producto')
    
    context = {
        'venta': venta,
        'detalles': detalles,
        'page_title': f'Detalle de Venta #{venta_id}'
    }
    return render(request, 'a_ventas/detalle_venta.html', context)

@require_POST
def anular_venta(request, venta_id):
    """Anula una venta (borrado lógico) y restaura el stock"""
    try:
        with transaction.atomic():
            venta = get_object_or_404(Ventas, pk=venta_id, borrado_venta=False)
            
            # Restaurar stock de cada producto
            detalles = DetallesVentas.objects.filter(id_venta=venta, borrado_det_v=False)
            for detalle in detalles:
                try:
                    stock = Stock.objects.get(
                        id_producto=detalle.id_producto,
                        id_loc_com=venta.id_loc_com,
                        borrado_pxlc=False
                    )
                    stock.stock_pxlc += detalle.cantidad
                    stock.save()
                except Stock.DoesNotExist:
                    pass
                
                # Marcar detalle como borrado
                detalle.borrado_det_v = True
                detalle.fh_borrado_det_v = timezone.now()
                detalle.save()
            
            # Marcar venta como borrada
            venta.borrado_venta = True
            venta.fh_borrado_venta = timezone.now()
            venta.save()
            
            messages.success(request, 'Venta anulada exitosamente')
            
    except Exception as e:
        messages.error(request, f'Error al anular la venta: {str(e)}')
    
    return redirect('a_ventas:listar_ventas')

# APIs para AJAX
@require_http_methods(["GET"])
def productos_disponibles_api(request):
    """API para buscar productos disponibles"""
    query = request.GET.get('q', '')
    
    if query:
        productos = Productos.objects.filter(
            borrado_prod=False,
            nombre_producto__icontains=query
        )[:10]
    else:
        productos = Productos.objects.filter(borrado_prod=False)[:10]
    
    data = [{
        'id': p.id_producto,
        'nombre': p.nombre_producto,
        'precio': str(p.precio_unit_prod) if p.precio_unit_prod else '0.00',
        'marca': p.id_marca.nombre_marca if p.id_marca else 'Sin marca'
    } for p in productos]
    
    return JsonResponse(data, safe=False)

@require_http_methods(["GET"])
def verificar_stock_api(request, producto_id, local_id):
    """API para verificar stock disponible"""
    try:
        stock = Stock.objects.get(
            id_producto_id=producto_id,
            id_loc_com_id=local_id,
            borrado_pxlc=False
        )
        return JsonResponse({
            'disponible': stock.stock_pxlc,
            'stock_minimo': stock.stock_min_pxlc
        })
    except Stock.DoesNotExist:
        return JsonResponse({'disponible': 0, 'stock_minimo': 0})

@require_http_methods(["GET"])
def cajas_disponibles_api(request, local_id):
    """API para obtener cajas disponibles de un local"""
    cajas = Cajas.objects.filter(
        id_loc_com_id=local_id,
        caja_abierta=True,
        borrado_caja=False
    )
    
    data = [{
        'id': c.id_caja,
        'numero': c.numero_caja
    } for c in cajas]
    
    return JsonResponse(data, safe=False)

def cierre_caja(request):
    """Vista para el cierre de caja y resumen de ventas"""
    hoy = date.today()
    
    # Obtener ventas del día
    ventas_hoy = Ventas.objects.filter(
        fh_venta__date=hoy,
        borrado_venta=False
    )
    
    total_ventas = sum(venta.total_venta for venta in ventas_hoy)
    cantidad_ventas = ventas_hoy.count()
    
    # Obtener arqueos de caja del día
    arqueos_hoy = ArqueoCaja.objects.filter(
        fh_apertura__date=hoy,
        cerrado=True
    )
    
    context = {
        'fecha': hoy,
        'ventas': ventas_hoy,
        'total_ventas': total_ventas,
        'cantidad_ventas': cantidad_ventas,
        'arqueos': arqueos_hoy,
        'page_title': 'Cierre de Caja'
    }
    
    return render(request, 'a_ventas/cierre_caja.html', context)

@require_http_methods(["GET"])
def ventas_del_dia_api(request):
    """API para obtener ventas del día actual"""
    hoy = date.today()
    
    ventas = Ventas.objects.filter(
        fh_venta__date=hoy,
        borrado_venta=False
    ).select_related('id_loc_com', 'id_empleado', 'id_caja')
    
    data = [{
        'id': v.id_venta,
        'local': v.id_loc_com.nombre_loc_com,
        'empleado': f"{v.id_empleado.nombre_emp} {v.id_empleado.apellido_emp}",
        'caja': v.id_caja.numero_caja if v.id_caja else 'N/A',
        'total': float(v.total_venta),
        'fecha': v.fh_venta.strftime('%H:%M:%S')
    } for v in ventas]
    
    return JsonResponse({'ventas': data, 'total': float(sum(v.total_venta for v in ventas))})