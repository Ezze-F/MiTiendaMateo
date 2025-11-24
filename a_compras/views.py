# ===============================
# IMPORTS
# ===============================
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db import models, transaction
from datetime import timedelta

# Formularios
from .forms import CompraForm, DetalleCompraFormSet

# Modelos
from .models import Compras, DetallesCompras
from a_central.models import Empleados, LocalesComerciales, Productos, Proveedores
from a_stock.models import Stock, LoteProducto, Proveedoresxproductos
from a_central.models import BilleterasVirtuales
from a_cajas.models import PagosCompras, MovimientosFinancieros
from .models import PedidosProveedor, DetallePedidosProveedor
from django.contrib import messages

# ===============================
# BLOQUE: COMPRAS
# ===============================

def listar_compras(request):
    """
    Vista principal de Compras:
    - Lista compras activas y eliminadas
    - Permite crear nueva compra
    - Permite cambiar estado de compra
    """
    empleado = Empleados.objects.filter(user_auth=request.user).first()
    if not empleado:
        return HttpResponse("Este usuario no está vinculado a un empleado.")

    compras_activas = Compras.objects.filter(borrado_compra=False).select_related(
        'id_loc_com', 'cuit_proveedor', 'legajo_empleado'
    ).order_by('-fecha_hora_compra')

    for compra in compras_activas:
        compra.ya_pagada = PagosCompras.objects.filter(id_compra=compra).exists() or \
            MovimientosFinancieros.objects.filter(id_compra=compra).exists()
    
    compras_eliminadas = Compras.objects.filter(borrado_compra=True).select_related(
        'id_loc_com', 'cuit_proveedor', 'legajo_empleado'
    ).order_by('-fh_borrado_c')

    show_modal = False

    # ===============================
    # CAMBIAR ESTADO DE COMPRA (AJAX)
    # ===============================
    if request.method == "POST" and "compra_id" in request.POST and "situacion_compra" in request.POST:
        compra_id = request.POST.get("compra_id")
        compra = get_object_or_404(Compras, pk=compra_id)
        nueva_situacion = request.POST.get("situacion_compra")

        if nueva_situacion not in dict(Compras.SITUACION_CHOICES):
            return JsonResponse({'success': False, 'error': 'Estado no válido.'}, status=400)

        compra.situacion_compra = nueva_situacion
        compra.save()

        return JsonResponse({'success': True, 'message': 'Estado actualizado correctamente.'})

    # ===============================
    # CREAR NUEVA COMPRA (AJAX)
    # ===============================
    elif request.method == "POST":
        compra_form = CompraForm(request.POST)
        detalle_formset = DetalleCompraFormSet(request.POST)

        if compra_form.is_valid() and detalle_formset.is_valid():
            crear_compra(compra_form, detalle_formset, empleado)
            return JsonResponse({'success': True, 'message': 'Compra registrada correctamente.'})

        return JsonResponse({'success': False, 'error': 'Datos inválidos.'}, status=400)

    # ===============================
    # MÉTODO GET → RENDER NORMAL
    # ===============================
    else:
        compra_form = CompraForm()
        detalle_formset = DetalleCompraFormSet()

    return render(request, 'a_compras/listar_compras.html', {
        'compras': compras_activas,
        'compras_eliminadas': compras_eliminadas,
        'compra_form': compra_form,
        'detalle_formset': detalle_formset,
        'show_modal': show_modal,
    })


def crear_compra(compra_form, detalle_formset, empleado):
    """
    Función auxiliar para crear una compra y sus detalles.
    """
    compra = compra_form.save(commit=False)
    compra.id_loc_com = compra_form.cleaned_data['local']
    compra.cuit_proveedor = compra_form.cleaned_data['proveedor']
    compra.legajo_empleado = empleado
    compra.fecha_hora_compra = timezone.now()
    compra.situacion_compra = "Pendiente"
    compra.monto_total = 0
    compra.save()

    total_estimado = 0
    detalles_a_guardar = detalle_formset.save(commit=False)

    for det in detalles_a_guardar:
        det.id_compra = compra
        det.precio_unitario = det.id_producto.precio_unit_prod or 0
        det.subtotal_est = det.cantidad * det.precio_unitario
        total_estimado += det.subtotal_est
        det.save()

    compra.monto_total = total_estimado
    compra.save()


# ===============================
# ELIMINAR COMPRA (AJAX)
# ===============================
def eliminar_compra(request, pk):
    compra = get_object_or_404(Compras, pk=pk)
    compra.borrado_compra = True
    compra.fh_borrado_c = timezone.now()
    compra.save()

    return JsonResponse({'success': True, 'message': 'Compra eliminada correctamente.'})


def detalle_compra(request, pk):
    compra = get_object_or_404(Compras, pk=pk)
    detalles_queryset = DetallesCompras.objects.filter(
        id_compra=compra
    ).select_related('id_producto', 'id_producto__id_marca')

    detalles = list(detalles_queryset)
    for d in detalles:
        d.subtotal = d.cantidad * d.precio_unitario

    total = sum(d.subtotal for d in detalles)

    return render(request, 'a_compras/detalle_compra.html', {
        'compra': compra,
        'detalles': detalles,
        'total': total,
    })


def ajax_locales_productos(request, proveedor_id):
    try:
        locales = LocalesComerciales.objects.filter(
            proveedoresxloccom__id_proveedor=proveedor_id,
            proveedoresxloccom__borrado_pxlc=False
        ).values('id_loc_com', 'nombre_loc_com')

        productos = Productos.objects.filter(
            proveedoresxproductos__id_proveedor=proveedor_id,
            proveedoresxproductos__borrado_pvxpr=False
        ).values('id_producto', 'nombre_producto')

        return JsonResponse({
            'locales': list(locales),
            'productos': list(productos)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def ajax_proveedores_por_local(request, local_id):
    proveedores = Proveedores.objects.filter(
        proveedoresxloccom__id_loc_com=local_id
    ).values('cuit_prov', 'nombre_prov')

    return JsonResponse({'proveedores': list(proveedores)})

from django.views.decorators.http import require_POST
from django.db import transaction
from a_cajas.models import PagosCompras, MovimientosFinancieros

@require_POST
def registrar_pago(request, compra_id):
    compra = get_object_or_404(Compras, pk=compra_id)

    # La compra debe estar completada
    if compra.situacion_compra != "Completada":
        return JsonResponse({"error": "La compra debe estar completada antes de registrarse el pago."}, status=400)

    # Evitar doble pago
    if PagosCompras.objects.filter(id_compra=compra).exists() or \
       MovimientosFinancieros.objects.filter(id_compra=compra).exists():
        return JsonResponse({"error": "Esta compra ya tiene registrado un pago."}, status=400)

    metodo = request.POST.get("metodo_pago")
    id_bv = request.POST.get("id_bv")

    with transaction.atomic():

        # =============================================
        # MÉTODO → BILLETERA VIRTUAL
        # =============================================
        if metodo == "Billetera":

            if not id_bv:
                return JsonResponse({"error": "Debe elegir una billetera virtual."}, status=400)

            billetera = BilleterasVirtuales.objects.select_for_update().get(pk=id_bv)

            # Verificar saldo suficiente
            if billetera.saldo_bv < compra.monto_total:
                return JsonResponse({"error": "La billetera no tiene saldo suficiente."}, status=400)

            # Descontar saldo
            billetera.saldo_bv -= compra.monto_total
            billetera.save()

            # Registrar pago
            PagosCompras.objects.create(
                id_compra=compra,
                id_bv=billetera,
                monto=compra.monto_total
            )

            # Crear movimiento financiero (EGRESO por compra)
            MovimientosFinancieros.objects.create(
                id_bv=billetera,
                id_compra=compra,
                medio_pago="BV",
                tipo_movimiento="EGRESO",
                concepto=f"Pago de compra #{compra.id_compra} con billetera virtual",
                monto=compra.monto_total
            )

        # =============================================
        # MÉTODO → EFECTIVO
        # =============================================
        elif metodo == "Efectivo":

            MovimientosFinancieros.objects.create(
                id_compra=compra,
                tipo_movimiento="EGRESO",
                medio_pago="EFECTIVO",
                concepto=f"Pago de compra #{compra.id_compra}",
                monto=compra.monto_total
            )
        
        else:
            return JsonResponse({"error": "Método de pago inválido."}, status=400)

    return JsonResponse({"message": "Pago registrado correctamente."})


def ajax_billeteras(request):
    billeteras = list(BilleterasVirtuales.objects.values("id_bv", "nombre_bv"))

    return JsonResponse({"billeteras": billeteras})









# =========================================================
# PARTE DE PEDIDOS PROVISORIOS
# =========================================================


# =========================================================
# Función auxiliar para calcular total estimado
# =========================================================
def actualizar_total_pedido(pedido):
    """
    Calcula el total estimado de un pedido provisorio y actualiza el campo
    total_estimado. También actualiza subtotal_est de cada detalle.
    """
    total = 0
    detalles = pedido.detallepedidosproveedor_set.filter(borrado_det_ped_prov=False)
    for det in detalles:
        precio = det.costo_est_unit or det.id_producto.precio_unit_prod or 0
        subtotal = det.cantidad_solicitada * precio
        total += subtotal
        # Guardar subtotal en detalle
        det.subtotal_est = subtotal
        det.save(update_fields=['subtotal_est'])
    pedido.total_estimado = total
    pedido.save(update_fields=['total_estimado'])
    return total

# =========================================================
# Listar pedidos provisorios
# =========================================================
def listar_pedidos_provisorios(request):
    pedidos = PedidosProveedor.objects.filter(borrado_ped_prov=False).select_related(
        'id_proveedor', 'id_loc_com', 'id_empleado'
    ).prefetch_related('detallepedidosproveedor_set__id_producto').order_by('-fh_pedido_prov')

    # Calcular total estimado de cada pedido
    for pedido in pedidos:
        actualizar_total_pedido(pedido)

    return render(request, 'a_compras/listar_pedidos_provisorios.html', {
        'pedidos': pedidos
    })

# =========================================================
# Detalle de un pedido provisorio
# =========================================================
def detalle_pedido_provisorio(request, pk):
    # Traemos el pedido con el proveedor y el local ya relacionados
    pedido = get_object_or_404(
        PedidosProveedor.objects.select_related('id_proveedor', 'id_loc_com'),
        pk=pk,
        borrado_ped_prov=False
    )

    # Calculamos el total estimado de los detalles
    actualizar_total_pedido(pedido)

    # Traemos los detalles con los productos relacionados
    detalles = DetallePedidosProveedor.objects.filter(
        id_pedido_prov=pedido,
        borrado_det_ped_prov=False
    ).select_related('id_producto')

    return render(request, 'a_compras/detalle_pedido_provisorio.html', {
        'pedido': pedido,
        'detalles': detalles,
    })


# =========================================================
# Confirmar pedido provisorio (genera compra)
# =========================================================
@transaction.atomic
def confirmar_pedido_provisorio(request, pk):
    pedido = get_object_or_404(PedidosProveedor, pk=pk, borrado_ped_prov=False)
    empleado = Empleados.objects.filter(user_auth=request.user).first()
    if not empleado:
        messages.error(request, "Usuario no vinculado a empleado.")
        return redirect('a_compras:listar_pedidos_provisorios')

    detalles_pedido = DetallePedidosProveedor.objects.filter(
        id_pedido_prov=pedido, borrado_det_ped_prov=False
    ).select_related('id_producto')

    if not detalles_pedido.exists():
        messages.error(request, "El pedido no tiene detalles válidos.")
        return redirect('a_compras:listar_pedidos_provisorios')

    # Crear la compra
    compra = Compras(
        id_loc_com=pedido.id_loc_com,
        cuit_proveedor=pedido.id_proveedor,
        legajo_empleado=empleado,
        fecha_hora_compra=timezone.now(),
        situacion_compra="Pendiente",
        monto_total=0
    )
    compra.save()

    total = 0
    for det in detalles_pedido:
        producto = det.id_producto
        cantidad = det.cantidad_solicitada or 0

        precio_unitario = det.costo_est_unit or (
            Proveedoresxproductos.objects.filter(id_proveedor=pedido.id_proveedor, id_producto=producto).first().costo_compra
            if Proveedoresxproductos.objects.filter(id_proveedor=pedido.id_proveedor, id_producto=producto).exists()
            else producto.precio_unit_prod
        )

        subtotal = cantidad * float(precio_unitario)
        total += subtotal

        DetallesCompras.objects.create(
            id_compra=compra,
            id_producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_unitario
        )

    compra.monto_total = total
    compra.save()

    # Borrado lógico del pedido provisorio
    pedido.borrado_ped_prov = True
    pedido.fh_borrado_ped_prov = timezone.now()
    pedido.save()
    detalles_pedido.update(borrado_det_ped_prov=True, fh_borrado_det_ped_prov=timezone.now())

    messages.success(request, f"Pedido {pedido.id_pedido_prov} confirmado: Compra #{compra.id_compra} creada correctamente.")
    return redirect('a_compras:listar_compras')


# =========================================================
# Generar pedidos automáticos
# =========================================================
@transaction.atomic
def generar_pedidos_automaticos(request):
    empleado = Empleados.objects.filter(user_auth=request.user).first()
    if not empleado:
        messages.error(request, "Usuario no vinculado a un empleado.")
        return redirect('a_compras:listar_pedidos_provisorios')

    # Productos con stock bajo
    bajo_stock = Stock.objects.filter(
        borrado_pxlc=False,
        stock_min_pxlc__gt=0,
        stock_pxlc__lt=models.F('stock_min_pxlc')
    ).select_related('id_producto', 'id_loc_com')

    if not bajo_stock.exists():
        messages.info(request, "No hay productos por debajo del stock mínimo.")
        return redirect('a_compras:listar_pedidos_provisorios')

    pedidos_dict = {}  # Clave: proveedor, Valor: pedido creado

    for st in bajo_stock:
        producto = st.id_producto

        # Buscar proveedor con menor precio para este producto
        mejor_rel = Proveedoresxproductos.objects.filter(
            id_producto=producto
        ).exclude(costo_compra__isnull=True).order_by('costo_compra').first()

        if not mejor_rel:
            # Si no hay relación con precio, saltar
            continue

        proveedor = mejor_rel.id_proveedor

        # Crear pedido si no existe aún para este proveedor
        pedido = pedidos_dict.get(proveedor.id_proveedor)
        if not pedido:
            pedido = PedidosProveedor.objects.create(
                id_proveedor=proveedor,
                id_loc_com=st.id_loc_com,
                id_empleado=empleado,
                fh_pedido_prov=timezone.now(),
                estado_pedido_prov="Pendiente",
                total_estimado=0,
                borrado_ped_prov=False
            )
            pedidos_dict[proveedor.id_proveedor] = pedido

        # Cantidad: doble del stock mínimo
        cantidad = max(2 * st.stock_min_pxlc, 1)

        # Crear detalle solo si no existe (por si hay productos repetidos)
        detalle, creado = DetallePedidosProveedor.objects.get_or_create(
            id_pedido_prov=pedido,
            id_producto=producto,
            defaults={
                'cantidad_solicitada': cantidad,
                'costo_est_unit': mejor_rel.costo_compra or producto.precio_unit_prod,
                'subtotal_est': cantidad * (mejor_rel.costo_compra or producto.precio_unit_prod),
                'borrado_det_ped_prov': False
            }
        )

        if not creado:
            # Si ya existía el detalle, actualizar cantidad y subtotal
            detalle.cantidad_solicitada = cantidad
            detalle.costo_est_unit = mejor_rel.costo_compra or producto.precio_unit_prod
            detalle.subtotal_est = cantidad * detalle.costo_est_unit
            detalle.borrado_det_ped_prov = False
            detalle.save(update_fields=['cantidad_solicitada', 'costo_est_unit', 'subtotal_est', 'borrado_det_ped_prov'])

    pedidos_creados = len(pedidos_dict)
    if pedidos_creados == 0:
        messages.info(request, "No se generaron pedidos automáticos.")
    else:
        messages.success(request, f"Se generaron {pedidos_creados} pedidos provisorios automáticamente.")

    return redirect('a_compras:listar_pedidos_provisorios')
