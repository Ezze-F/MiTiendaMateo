import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
from a_central.models import Marcas, Proveedores, LocalesComerciales, Productos
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.views.decorators.http import require_POST
from a_compras.models import DetallesCompras, Compras
from a_cajas.models import MovimientosFinancieros, PagosCompras
from django.db import transaction

# =========================
# DECORADORES DE SEGURIDAD (FALTANTES)
# =========================
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required

@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def index(request):
    """
    Vista principal de la aplicación de stock.
    """
    # Ejemplo de uso de modelos: Obtener todas las marcas
    marcas = Marcas.objects.all() 
    context = {'marcas': marcas}
    
    # Aquí iría tu lógica de vista. Por ahora, solo devuelve una plantilla de ejemplo.
    return render(request, 'a_stock/index.html', context)

from django.shortcuts import render, redirect
from .models import ObservacionStock

from django.contrib import messages
from .models import ObservacionStock
from datetime import datetime

from .models import Stock, LoteProducto, ObservacionStock
from a_central.models import Productos, LocalesComerciales


# ===============================
# LISTAR OBSERVACIONES MODERNO
# ===============================
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ObservacionStock
from datetime import datetime


from django.shortcuts import render
from .models import ObservacionStock

@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def lista_observaciones(request):
    # ---- FILTROS ----
    producto = request.GET.get('producto')
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')

    # Cargar observaciones con lote y producto
    observaciones = ObservacionStock.objects.select_related(
        "lote",
        "lote__id_producto"
    ).order_by('-fecha')

    # ---- FILTRO POR PRODUCTO ----
    if producto:
        observaciones = observaciones.filter(
            lote__id_producto__nombre_producto__icontains=producto
        )

    # ---- FILTRO POR FECHAS ----
    if desde:
        observaciones = observaciones.filter(fecha__gte=desde)

    if hasta:
        observaciones = observaciones.filter(fecha__lte=hasta)

    # ---- RESÚMENES ----
    total_obs = observaciones.count()
    perdidas = observaciones.filter(motivo__icontains="Pérdida").count()
    roturas = observaciones.filter(motivo__icontains="Rotura").count()
    vencimientos = observaciones.filter(motivo__icontains="Vencimiento").count()

    context = {
        "observaciones": observaciones,
        "producto_filtro": producto or "",
        "desde": desde or "",
        "hasta": hasta or "",
        "total_obs": total_obs,
        "perdidas": perdidas,
        "roturas": roturas,
        "vencimientos": vencimientos,
    }

    return render(request, "a_stock/observacion_list.html", context)




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import ObservacionStock, LoteProducto, Stock
from a_central.models import Productos, LocalesComerciales

from datetime import date

@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def registrar_observacion(request):
    producto_id = request.GET.get("producto")
    productos = Productos.objects.filter(borrado_prod=False)

    producto_sel = None
    lotes = []

    # Si el usuario seleccionó un producto → cargar solo lotes activos
    if producto_id:
        producto_sel = Productos.objects.filter(pk=producto_id).first()
        lotes = LoteProducto.objects.filter(
            id_producto=producto_sel,
            activo=True,
            borrado_logico=False
        )

    if request.method == "POST":
        lote_id = request.POST.get("lote")
        motivo = request.POST.get("motivo")
        descripcion = request.POST.get("descripcion")
        fecha = request.POST.get("fecha")
        cantidad = int(request.POST.get("cantidad"))

        lote = get_object_or_404(LoteProducto, pk=lote_id)

        # Crear observación
        ObservacionStock.objects.create(
            lote=lote,
            motivo=motivo,
            descripcion=descripcion,
            fecha=fecha,
            cantidad=cantidad
        )

        # Descontar stock del lote
        lote.cantidad -= cantidad
        if lote.cantidad < 0:
            lote.cantidad = 0
        lote.save()

        # También actualizamos stock general
        stock = Stock.objects.filter(
            id_producto=lote.id_producto,
            id_loc_com=lote.id_loc_com
        ).first()

        if stock:
            stock.stock_pxlc -= cantidad
            if stock.stock_pxlc < 0:
                stock.stock_pxlc = 0
            stock.save()

        messages.success(request, "Observación registrada correctamente.")
        return redirect("a_stock:lista_observaciones")

    return render(request, "a_stock/observacion_form.html", {
        "productos": productos,
        "producto_sel": producto_sel,
        "lotes": lotes,
    })




# =========================
# ELIMINAR OBSERVACIÓN
# =========================

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def eliminar_observacion(request, id):
    observacion = get_object_or_404(ObservacionStock, id=id)
    observacion.delete()
    messages.success(request, "Observación eliminada correctamente.")
    return redirect("a_stock:lista_observaciones")


# =========================
# LISTAR STOCK (Actualizada con lotes)
# =========================
from datetime import date, timedelta
from .models import Stock, LoteProducto
from a_central.models import Productos, LocalesComerciales
from django.shortcuts import render
from django.db import models

@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def lista_stock(request):
    productos = Productos.objects.filter(borrado_prod=False)
    locales = LocalesComerciales.objects.filter(borrado_loc_com=False)
    stocks = Stock.objects.filter(borrado_pxlc=False).select_related('id_producto', 'id_loc_com')

    # 🔍 Filtros
    buscar = request.GET.get('buscar')
    producto = request.GET.get('producto')
    local = request.GET.get('local')

    if buscar:
        stocks = stocks.filter(
            id_producto__nombre_producto__icontains=buscar
        ) | stocks.filter(
            id_loc_com__nombre_loc_com__icontains=buscar
        )

    if producto:
        stocks = stocks.filter(id_producto_id=producto)

    if local:
        stocks = stocks.filter(id_loc_com_id=local)

    # 📅 Control de fechas
    today = date.today()
    proximo = today + timedelta(days=30)

    # 🔗 Vincular lotes activos + sincronizar stock + calcular vencimiento
    for s in stocks:
        # 1️⃣ Obtener todos los lotes activos del producto en ese local
        lotes_activos = LoteProducto.objects.filter(
            id_producto=s.id_producto,
            id_loc_com=s.id_loc_com,
            activo=True
        ).order_by('fecha_vencimiento')

        # 2️⃣ Actualizar el stock en base a los lotes activos
        total_lotes = lotes_activos.aggregate(total=models.Sum('cantidad'))['total'] or 0
        if s.stock_pxlc != total_lotes:
            s.stock_pxlc = total_lotes
            s.save()

        # 3️⃣ Guardar datos derivados para la plantilla
        s.lotes_activos = lotes_activos
        s.lotes_count = lotes_activos.count()
        s.lote_proximo = lotes_activos.first() if lotes_activos.exists() else None

    context = {
        'stocks': stocks,
        'productos': productos,
        'locales': locales,
        'today': today,
        'proximo': proximo,
    }

    return render(request, 'a_stock/stock_list.html', context)




# =========================
# NUEVO STOCK
# =========================
@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def nuevo_stock(request):
    productos = Productos.objects.filter(borrado_prod=False)
    locales = LocalesComerciales.objects.filter(borrado_loc_com=False)

    if request.method == 'POST':
        id_producto = request.POST.get('producto')
        id_local = request.POST.get('local')
        stock_pxlc = request.POST.get('stock_pxlc')
        stock_min_pxlc = request.POST.get('stock_min_pxlc')

        Stock.objects.create(
            id_producto_id=id_producto,
            id_loc_com_id=id_local,
            stock_pxlc=stock_pxlc,
            stock_min_pxlc=stock_min_pxlc
        )
        return redirect('a_stock:lista_stock')

    return render(request, 'a_stock/stock_form.html', {
        'productos': productos,
        'locales': locales,
        'accion': 'Nuevo Stock'
    })

# =========================
# EDITAR STOCK
# =========================
@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def editar_stock(request, id):
    stock = get_object_or_404(Stock, id_stock_sucursal=id)
    productos = Productos.objects.filter(borrado_prod=False)
    locales = LocalesComerciales.objects.filter(borrado_loc_com=False)

    if request.method == 'POST':
        stock.id_producto_id = request.POST.get('producto')
        stock.id_loc_com_id = request.POST.get('local')
        stock.stock_pxlc = request.POST.get('stock_pxlc')
        stock.stock_min_pxlc = request.POST.get('stock_min_pxlc')
        stock.save()
        return redirect('a_stock:lista_stock')

    return render(request, 'a_stock/stock_form.html', {
        'stock': stock,
        'productos': productos,
        'locales': locales,
        'accion': 'Editar Stock'
    })

# =========================
# ELIMINAR STOCK (borrado lógico)
# =========================
@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def eliminar_stock(request, id):
    stock = get_object_or_404(Stock, id_stock_sucursal=id)
    stock.borrado_pxlc = True
    stock.fh_borrado_pxlc = timezone.now()
    stock.save()
    return redirect('a_stock:lista_stock')


#=========================
# OBTENER STOCK EN FORMATO JSON
#=========================


from django.http import JsonResponse
from django.utils import timezone
from .models import Stock

@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def obtener_stock_json(request):
    stock_items = Stock.objects.select_related('id_producto', 'id_loc_com').values(
        'id_producto__nombre_producto',
        'id_producto__fecha_venc_prod',
        'stock_pxlc',
        'stock_min_pxlc'
    )
    return JsonResponse(list(stock_items), safe=False)

#--------------------------------
# Vistas para lotes y vencimientos
#--------------------------------

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from a_central.models import Productos, LocalesComerciales
from .models import LoteProducto
from datetime import date, timedelta

# --------------------------------
# Vistas para lotes y vencimientos
# --------------------------------

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from datetime import date, timedelta

from .models import Stock, LoteProducto
from a_central.models import Productos, LocalesComerciales
from django.db import models


# ================================
# LISTAR LOTES (ACTIVOS + TAB RESTAURAR)
# ================================
@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def ver_lotes(request, id_producto):
    producto = get_object_or_404(Productos, pk=id_producto)

    lotes_activos = LoteProducto.objects.filter(
        id_producto=producto,
        activo=True,
        borrado_logico=False
    ).order_by("fecha_vencimiento")

    lotes_eliminados = LoteProducto.objects.filter(
        id_producto=producto,
        activo=False,
        borrado_logico=True
    ).order_by("-fecha_ingreso")

    today = date.today()
    proximo = today + timedelta(days=30)

    context = {
        'producto': producto,
        'lotes_activos': lotes_activos,
        'lotes_eliminados': lotes_eliminados,
        'today': today,
        'proximo': proximo,
        'lotes_vencidos_count': lotes_activos.filter(fecha_vencimiento__lt=today).count(),
        'lotes_por_vencer_count': lotes_activos.filter(fecha_vencimiento__range=[today, proximo]).count(),
        'lotes_vigentes_count': lotes_activos.filter(fecha_vencimiento__gt=proximo).count(),
    }

    return render(request, 'a_stock/lote_list.html', context)


# ================================
# CREAR LOTE
# ================================
@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def nuevo_lote(request, id_producto):
    producto = get_object_or_404(Productos, pk=id_producto)
    locales = LocalesComerciales.objects.filter(borrado_loc_com=False)

    if request.method == 'POST':
        cantidad = request.POST.get('cantidad')
        id_loc_com = request.POST.get('id_loc_com')
        fecha_ingreso = request.POST.get('fecha_ingreso')
        fecha_vencimiento = request.POST.get('fecha_vencimiento')

        # Generar número de lote automáticamente
        ultimo = LoteProducto.objects.all().order_by('-id_lote').first()
        numero_lote = f"LOT-{ultimo.id_lote + 1 if ultimo else 1:04d}"

        LoteProducto.objects.create(
            id_producto=producto,
            id_loc_com_id=id_loc_com,
            numero_lote=numero_lote,
            cantidad=cantidad,
            fecha_ingreso=fecha_ingreso,
            fecha_vencimiento=fecha_vencimiento,
            activo=True,
            borrado_logico=False
        )

        messages.success(request, "Lote creado correctamente.")
        return redirect('a_stock:ver_lotes', id_producto=producto.id_producto)

    return render(request, 'a_stock/lote_form.html', {
        'producto': producto,
        'locales': locales
    })


# ================================
# EDITAR LOTE
# ================================
@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def editar_lote(request, id_lote):
    lote = get_object_or_404(LoteProducto, pk=id_lote)
    locales = LocalesComerciales.objects.filter(borrado_loc_com=False)

    if request.method == 'POST':
        lote.cantidad = request.POST.get('cantidad')
        lote.id_loc_com_id = request.POST.get('id_loc_com')
        lote.fecha_ingreso = request.POST.get('fecha_ingreso')
        lote.fecha_vencimiento = request.POST.get('fecha_vencimiento')
        lote.save()

        messages.success(request, "Lote actualizado correctamente.")
        return redirect('a_stock:ver_lotes', id_producto=lote.id_producto.id_producto)

    return render(request, 'a_stock/lote_form.html', {
        'lote': lote,
        'producto': lote.id_producto,
        'locales': locales
    })


# ================================
# ELIMINAR LOTE (BORRADO LÓGICO)
# ================================
@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def eliminar_lote(request, id_lote):
    lote = get_object_or_404(LoteProducto, pk=id_lote)

    lote.activo = False
    lote.borrado_logico = True
    lote.save()

    messages.success(request, f"Lote {lote.numero_lote} eliminado correctamente.")

    return redirect('a_stock:ver_lotes', id_producto=lote.id_producto.id_producto)


# ================================
# REACTIVAR LOTE ELIMINADO
# ================================
@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
def reactivar_lote(request, id_lote):
    lote = get_object_or_404(LoteProducto, pk=id_lote)

    lote.activo = True
    lote.borrado_logico = False
    lote.save()

    messages.success(request, f"Lote {lote.numero_lote} restaurado correctamente.")

    return redirect('a_stock:ver_lotes', id_producto=lote.id_producto.id_producto)


# ================================
# SEÑALES — Sincronizar stock automáticamente
# ================================
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender=LoteProducto)
def actualizar_stock_lote(sender, instance, **kwargs):
    """
    Actualiza el stock cuando un lote se crea, edita o se reactiva/desactiva.
    """
    total_lotes_activos = LoteProducto.objects.filter(
        id_producto=instance.id_producto,
        id_loc_com=instance.id_loc_com,
        activo=True,
        borrado_logico=False
    ).aggregate(total=models.Sum('cantidad'))['total'] or 0

    stock, _ = Stock.objects.get_or_create(
        id_producto=instance.id_producto,
        id_loc_com=instance.id_loc_com,
        defaults={'stock_pxlc': 0, 'stock_min_pxlc': 0, 'borrado_pxlc': False}
    )

    stock.stock_pxlc = total_lotes_activos
    stock.save()


@receiver(post_delete, sender=LoteProducto)
def reducir_stock_al_eliminar_lote(sender, instance, **kwargs):
    """
    Actualiza stock si el lote fuera eliminado físicamente (no lógico).
    """
    stock = Stock.objects.filter(
        id_producto=instance.id_producto,
        id_loc_com=instance.id_loc_com
    ).first()

    if stock:
        total_lotes_activos = LoteProducto.objects.filter(
            id_producto=instance.id_producto,
            id_loc_com=instance.id_loc_com,
            activo=True,
            borrado_logico=False
        ).aggregate(total=models.Sum('cantidad'))['total'] or 0

        stock.stock_pxlc = total_lotes_activos
        stock.save()


# ================================
# CARGAR COMPRAS EN STOCK
# ================================
@login_required
@permission_required('a_central.view_empleados', raise_exception=True)
#CODIGO PARA IMPLEMENTAR LA CREACION DE LOTES CON EL REGISTRO DE PAGO
def cargar_compras(request):

    compras = Compras.objects.filter(
        situacion_compra="Completada",
        borrado_compra=False
    )

    compras_finales = []

    for c in compras:

        # ✔ Ya pagada
        pagada = PagosCompras.objects.filter(id_compra=c).exists() or \
                 MovimientosFinancieros.objects.filter(id_compra=c).exists()

        if not pagada:
            continue

        # ✔ Ver si ya tiene lotes creados
        detalles = DetallesCompras.objects.filter(id_compra=c)

        productos_ids = detalles.values_list("id_producto_id", flat=True)

        lotes_existentes = LoteProducto.objects.filter(
            id_producto_id__in=productos_ids,
            id_loc_com=c.id_loc_com,
        ).exists()

        if lotes_existentes:
            # ❌ Ya fue cargada → NO se muestra
            continue

        compras_finales.append(c)

    return render(request, "a_stock/cargar_compras.html", {
        "compras": compras_finales
    })

@require_POST
def procesar_compra_en_stock(request, compra_id):
    try:
        compra = get_object_or_404(Compras, pk=compra_id)
        detalles = DetallesCompras.objects.filter(id_compra=compra)

        with transaction.atomic():
            for d in detalles:
                fecha_vto = request.POST.get(f"vto_{d.id_detalle_compra}")
                if not fecha_vto:
                    return JsonResponse({"error": f"Falta fecha de vencimiento para {d.id_producto.nombre_producto}"}, status=400)

                LoteProducto.objects.create(
                    id_producto=d.id_producto,
                    id_loc_com=compra.id_loc_com,
                    cantidad=d.cantidad,
                    fecha_ingreso=timezone.now(),   # DateTime completo
                    fecha_vencimiento=fecha_vto
                )

        return JsonResponse({"success": "Compra cargada en stock correctamente."})
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
