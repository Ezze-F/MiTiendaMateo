from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.template.loader import render_to_string
from datetime import datetime, date
from decimal import Decimal
import json
from .models import Ventas, DetallesVentas
from .forms import VentaForm, DetalleVentaForm
from a_central.models import Productos, Empleados, LocalesComerciales, BilleterasVirtuales
from a_stock.models import Stock, LoteProducto
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

def reducir_stock_de_lotes(id_producto, id_loc_com, cantidad):
    """
    Reduce stock de los lotes con vencimiento más cercano primero
    Retorna True si se pudo reducir completamente, False si no hay suficiente stock
    """
    # Obtener lotes activos ordenados por fecha de vencimiento (más cercano primero)
    lotes = LoteProducto.objects.filter(
        id_producto_id=id_producto,
        id_loc_com_id=id_loc_com,
        activo=True,
        borrado_logico=False
    ).order_by('fecha_vencimiento')
    
    cantidad_restante = cantidad
    
    for lote in lotes:
        if cantidad_restante <= 0:
            break
            
        if lote.cantidad >= cantidad_restante:
            # Este lote tiene suficiente para cubrir lo que queda
            lote.cantidad -= cantidad_restante
            lote.save()
            cantidad_restante = 0
        else:
            # Este lote no tiene suficiente, tomamos todo lo que tiene
            cantidad_restante -= lote.cantidad
            lote.cantidad = 0
            lote.save()
    
    return cantidad_restante == 0

def registrar_venta(request):
    """Registra una nueva venta con reducción de stock por lotes"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                id_loc_com = request.POST.get('id_loc_com')
                id_caja = request.POST.get('id_caja')
                id_empleado = request.POST.get('id_empleado')
                tipo_venta = request.POST.get('tipo_venta', 'EFECTIVO')
                id_billetera = request.POST.get('id_billetera')  # Nuevo: billetera seleccionada
                
                # Validar campos requeridos
                if not all([id_loc_com, id_caja, id_empleado]):
                    messages.error(request, 'Todos los campos son requeridos')
                    return redirect('a_ventas:registrar_venta')
                
                # Validar billetera para ventas BV
                if tipo_venta == 'BV' and not id_billetera:
                    messages.error(request, 'Debe seleccionar una billetera virtual para ventas BV')
                    return redirect('a_ventas:registrar_venta')
                
                # Crear la venta
                venta = Ventas(
                    id_loc_com_id=id_loc_com,
                    id_caja_id=id_caja,
                    id_empleado_id=id_empleado,
                    fh_venta=timezone.now(),
                    total_venta=0
                )
                venta.save()
                
                # Procesar detalles de venta
                detalles_data = request.POST.getlist('detalles')
                total_venta = Decimal('0.00')
                
                for detalle_str in detalles_data:
                    if detalle_str:
                        try:
                            producto_id, cantidad, precio = detalle_str.split('|')
                            producto_id = int(producto_id)
                            cantidad = int(cantidad)
                            precio = Decimal(precio)
                            
                            # VERIFICAR STOCK TOTAL antes de procesar
                            stock_total = Stock.objects.get(
                                id_producto_id=producto_id,
                                id_loc_com_id=id_loc_com,
                                borrado_pxlc=False
                            )
                            
                            if stock_total.stock_pxlc < cantidad:
                                raise Exception(
                                    f"Stock insuficiente. Solicitado: {cantidad}, Disponible: {stock_total.stock_pxlc}"
                                )
                            
                            # REDUCIR STOCK DE LOTES
                            if not reducir_stock_de_lotes(producto_id, id_loc_com, cantidad):
                                raise Exception(
                                    f"Error al reducir stock de lotes para el producto ID {producto_id}"
                                )
                            
                            # Crear detalle de venta
                            detalle = DetallesVentas(
                                id_venta=venta,
                                id_producto_id=producto_id,
                                cantidad=cantidad,
                                precio_unitario_venta=precio,
                                subtotal=cantidad * precio
                            )
                            detalle.save()
                            
                            total_venta += detalle.subtotal
                            
                        except Stock.DoesNotExist:
                            raise Exception(f"Producto ID {producto_id} sin stock en este local")
                        except ValueError as e:
                            raise Exception(f"Error en formato de detalle: {detalle_str}")
                
                # Validar que haya al menos un producto
                if total_venta == 0:
                    venta.delete()  # Eliminar venta vacía
                    raise Exception("Debe agregar al menos un producto a la venta")
                
                # Actualizar total de la venta
                venta.total_venta = total_venta
                venta.save()
                
                # Registrar movimiento financiero según el tipo de venta
                if venta.id_caja:
                    arqueo_activo = ArqueoCaja.objects.filter(
                        id_caja=venta.id_caja,
                        fh_cierre__isnull=True
                    ).first()
                    
                    if arqueo_activo:
                        medio_pago = 'BILLETERA_VIRTUAL' if tipo_venta == 'BV' else 'EFECTIVO'
                        movimiento = MovimientosFinancieros.objects.create(
                            id_arqueo=arqueo_activo,
                            medio_pago=medio_pago,
                            tipo_movimiento='INGRESO',
                            concepto=f'Venta #{venta.id_venta} ({tipo_venta})',
                            monto=total_venta,
                            fh_movimiento=timezone.now()
                        )
                
              # ACTUALIZAR SALDO DE BILLETERA VIRTUAL SI ES VENTA BV
                billetera = None
                if tipo_venta == 'BV' and id_billetera:
                    try:
                        billetera = BilleterasVirtuales.objects.get(pk=id_billetera)
                        billetera.saldo_bv += total_venta
                        billetera.save()
                    except BilleterasVirtuales.DoesNotExist:
                        raise Exception("Billetera virtual seleccionada no existe")
                
                mensaje = f'Venta {tipo_venta} registrada exitosamente. Total: ${total_venta:.2f}'
                if tipo_venta == 'BV' and billetera:
                    mensaje += f' - Billetera: {billetera.nombre_bv}'
                messages.success(request, mensaje)
                return redirect('a_ventas:detalle_venta', venta_id=venta.id_venta)
                
        except Exception as e:
            messages.error(request, f'Error al registrar la venta: {str(e)}')
    
        # GET request - mostrar formulario vacío
        form = VentaForm()
        locales = LocalesComerciales.objects.filter(borrado_loc_com=False)
        empleados = Empleados.objects.filter(borrado_emp=False)
        billeteras = BilleterasVirtuales.objects.filter(borrado_bv=False)
        
        context = {
            'form': form,
            'locales': locales,
            'empleados': empleados,
            'billeteras': billeteras,
            'page_title': 'Registrar Nueva Venta'
        }
        return render(request, 'a_ventas/registrar_venta.html', context)
    
    # GET request - mostrar formulario vacío
    form = VentaForm()
    locales = LocalesComerciales.objects.filter(borrado_loc_com=False)
    empleados = Empleados.objects.filter(borrado_emp=False)
    billeteras = BilleterasVirtuales.objects.filter(borrado_bv=False)  # Para el select de billeteras
    
    context = {
        'form': form,
        'locales': locales,
        'empleados': empleados,
        'billeteras': billeteras,  # Nuevo: pasar billeteras al template
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
    
    # Determinar tipo de venta basado en movimientos financieros
    tipo_venta = 'EFECTIVO'
    billetera_utilizada = None
    
    try:
        movimiento = MovimientosFinancieros.objects.filter(
            concepto__contains=f'Venta #{venta_id}'
        ).first()
        if movimiento and 'BV' in movimiento.concepto:
            tipo_venta = 'BV'
            # Podríamos intentar extraer info de billetera del concepto si la guardamos
    except:
        pass
    
    context = {
        'venta': venta,
        'detalles': detalles,
        'tipo_venta': tipo_venta,
        'billetera_utilizada': billetera_utilizada,
        'page_title': f'Detalle de Venta #{venta_id}'
    }
    return render(request, 'a_ventas/detalle_venta.html', context)

def detalle_venta(request, venta_id):
    """Muestra el detalle de una venta específica"""
    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetallesVentas.objects.filter(
        id_venta=venta, 
        borrado_det_v=False
    ).select_related('id_producto')
    
    # Determinar tipo de venta basado en movimientos financieros
    tipo_venta = 'EFECTIVO'  # Por defecto
    try:
        movimiento = MovimientosFinancieros.objects.filter(
            concepto__contains=f'Venta #{venta_id}'
        ).first()
        if movimiento and 'BV' in movimiento.concepto:
            tipo_venta = 'BV'
    except:
        pass
    
    context = {
        'venta': venta,
        'detalles': detalles,
        'tipo_venta': tipo_venta,  # Pasamos el tipo calculado al template
        'page_title': f'Detalle de Venta #{venta_id}'
    }
    return render(request, 'a_ventas/detalle_venta.html', context)

def imprimir_ticket(request, venta_id):
    """Genera un ticket de venta estilo supermercado"""
    venta = get_object_or_404(Ventas, pk=venta_id)
    detalles = DetallesVentas.objects.filter(
        id_venta=venta, 
        borrado_det_v=False
    ).select_related('id_producto')
    
    # Determinar tipo de venta
    tipo_venta = 'EFECTIVO'
    try:
        movimiento = MovimientosFinancieros.objects.filter(
            concepto__contains=f'Venta #{venta_id}'
        ).first()
        if movimiento and 'BV' in movimiento.concepto:
            tipo_venta = 'BV'
    except:
        pass
    
    context = {
        'venta': venta,
        'detalles': detalles,
        'tipo_venta': tipo_venta,
    }
    
    # Renderizar como HTML para impresión
    html_content = render_to_string('a_ventas/ticket_venta.html', context)
    
    response = HttpResponse(html_content)
    return response

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
    """Anula una venta (borrado lógico) y restaura el stock en lotes"""
    try:
        with transaction.atomic():
            venta = get_object_or_404(Ventas, pk=venta_id, borrado_venta=False)
            
            # Restaurar stock de cada producto en lotes
            detalles = DetallesVentas.objects.filter(id_venta=venta, borrado_det_v=False)
            for detalle in detalles:
                # Buscar lotes activos para restaurar el stock
                lotes_activos = LoteProducto.objects.filter(
                    id_producto=detalle.id_producto,
                    id_loc_com=venta.id_loc_com,
                    activo=True,
                    borrado_logico=False
                ).order_by('fecha_vencimiento')
                
                cantidad_restaurar = detalle.cantidad
                
                for lote in lotes_activos:
                    if cantidad_restaurar <= 0:
                        break
                    
                    # Restaurar en este lote
                    lote.cantidad += cantidad_restaurar
                    lote.save()
                    cantidad_restaurar = 0
                
                # Si todavía queda stock por restaurar, crear un nuevo lote
                if cantidad_restaurar > 0:
                    # Crear un nuevo lote con la fecha actual
                    nuevo_lote = LoteProducto(
                        id_producto=detalle.id_producto,
                        id_loc_com=venta.id_loc_com,
                        cantidad=cantidad_restaurar,
                        fecha_ingreso=timezone.now().date(),
                        fecha_vencimiento=timezone.now().date() + timezone.timedelta(days=365),  # 1 año por defecto
                        activo=True
                    )
                    nuevo_lote.save()
                
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

# Vistas que devuelven JSON (simulan APIs)
@require_http_methods(["GET"])
def productos_disponibles_api(request):
    """Devuelve productos disponibles en formato JSON"""
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
    """Verifica stock disponible para un producto en un local"""
    try:
        stock = Stock.objects.get(
            id_producto_id=producto_id,
            id_loc_com_id=local_id,
            borrado_pxlc=False
        )
        
        producto = Productos.objects.get(id_producto=producto_id)
        
        # Obtener información de lotes para mostrar vencimientos
        lotes = LoteProducto.objects.filter(
            id_producto_id=producto_id,
            id_loc_com_id=local_id,
            activo=True,
            borrado_logico=False
        ).order_by('fecha_vencimiento')[:5]  # Solo los 5 lotes más próximos a vencer
        
        lotes_info = []
        for lote in lotes:
            lotes_info.append({
                'lote': lote.numero_lote,
                'cantidad': lote.cantidad,
                'vencimiento': lote.fecha_vencimiento.strftime('%d/%m/%Y'),
                'dias_restantes': (lote.fecha_vencimiento - timezone.now().date()).days
            })
        
        return JsonResponse({
            'disponible': stock.stock_pxlc,
            'stock_minimo': stock.stock_min_pxlc,
            'producto_nombre': producto.nombre_producto,
            'producto_precio': str(producto.precio_unit_prod) if producto.precio_unit_prod else '0.00',
            'lotes': lotes_info
        })
    except Stock.DoesNotExist:
        return JsonResponse({
            'disponible': 0, 
            'stock_minimo': 0,
            'producto_nombre': 'Producto no encontrado',
            'producto_precio': '0.00',
            'lotes': []
        })
    except Productos.DoesNotExist:
        return JsonResponse({
            'disponible': 0,
            'stock_minimo': 0, 
            'producto_nombre': 'Producto no existe',
            'producto_precio': '0.00',
            'lotes': []
        })

@require_http_methods(["GET"])
def cajas_disponibles_api(request, local_id):
    """Devuelve cajas disponibles de un local"""
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
    """Devuelve ventas del día actual en formato JSON"""
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