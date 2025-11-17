from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from .forms import CompraForm, DetalleCompraFormSet
from .models import Compras, DetallesCompras
from a_central.models import Empleados

from .models import PedidosProveedor, DetallePedidosProveedor


def listar_compras(request):
    """
    Vista principal de Compras:
    - Muestra compras activas y eliminadas
    - Permite crear nueva compra
    - Permite cambiar estado de compra
    """

    empleado = Empleados.objects.filter(user_auth=request.user).first()

    if not empleado:
        return HttpResponse("Este usuario no está vinculado a un empleado. Configúrelo en el panel de administración.")

    # Compras activas y eliminadas
    compras_activas = Compras.objects.filter(borrado_compra=False).select_related(
        'id_loc_com', 'cuit_proveedor', 'legajo_empleado'
    ).order_by('-fecha_hora_compra')

    compras_eliminadas = Compras.objects.filter(borrado_compra=True).select_related(
        'id_loc_com', 'cuit_proveedor', 'legajo_empleado'
    ).order_by('-fh_borrado_c')

    show_modal = False

    # POST para cambiar estado de compra
    if request.method == "POST" and "compra_id" in request.POST and "situacion_compra" in request.POST:
        compra_id = request.POST.get("compra_id")
        compra = get_object_or_404(Compras, pk=compra_id)
        nueva_situacion = request.POST.get("situacion_compra")
        if nueva_situacion in dict(Compras.SITUACION_CHOICES):
            compra.situacion_compra = nueva_situacion
            compra.save()
        return redirect('a_compras:listar_compras')

    # POST para crear nueva compra
    elif request.method == "POST":
        compra_form = CompraForm(request.POST)
        detalle_formset = DetalleCompraFormSet(request.POST)
        if compra_form.is_valid() and detalle_formset.is_valid():
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
            return redirect('a_compras:listar_compras')
        else:
            show_modal = True
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


def eliminar_compra(request, pk):
    """
    Realiza borrado lógico de la compra
    """
    compra = get_object_or_404(Compras, pk=pk)
    compra.borrado_compra = True
    compra.fh_borrado_c = timezone.now()
    compra.save()
    return redirect('a_compras:listar_compras')

def detalle_compra(request, pk):
    compra = get_object_or_404(Compras, pk=pk)
    detalles_queryset = DetallesCompras.objects.filter(
        id_compra=compra
    ).select_related('id_producto', 'id_producto__id_marca')

    # Convertir queryset a lista real
    detalles = list(detalles_queryset)

    # Calcular subtotal y total
    for d in detalles:
        d.subtotal = d.cantidad * d.precio_unitario

    total = sum(d.subtotal for d in detalles)

    return render(request, 'a_compras/detalle_compra.html', {
        'compra': compra,
        'detalles': detalles,
        'total': total,
    })

#PEDIDOS 
def listar_pedidos_provisorios(request):
    """
    Vista que muestra los pedidos provisorios.
    """
    pedidos = (
        PedidosProveedor.objects.filter(borrado_ped_prov=False)
        .select_related('id_proveedor', 'id_loc_com', 'id_empleado')
        .prefetch_related('detallepedidosproveedor_set__id_producto')
        .order_by('-fh_pedido_prov')
    )

    return render(request, 'a_compras/listar_pedidos_provisorios.html', {
        'pedidos': pedidos
    })
