from django.contrib import admin
from .models import Compras, DetallesCompras

# Register your models here.

@admin.register(Compras)
class ComprasAdmin(admin.ModelAdmin):
    list_display = ('id_compra', 'id_loc_com', 'cuit_proveedor', 'legajo_empleado', 'fecha_hora_compra', 'monto_total', 'situacion_compra')
    list_filter = ('id_loc_com', 'cuit_proveedor', 'situacion_compra')
    search_fields = ('id_compra', 'cuit_proveedor__nombre_prov', 'legajo_empleado__nombre_empleado', 'id_loc_com__nombre_loc_com')
    raw_id_fields = ('id_loc_com', 'cuit_proveedor', 'legajo_empleado',)
    list_select_related = ('id_loc_com', 'cuit_proveedor', 'legajo_empleado',)

@admin.register(DetallesCompras)
class DetallesComprasAdmin(admin.ModelAdmin):
    list_display = ('id_detalle_compra', 'id_compra', 'id_producto', 'cantidad', 'precio_unitario')
    list_filter = ('id_compra', 'id_producto')
    raw_id_fields = ('id_compra', 'id_producto',)
    list_select_related = ('id_compra', 'id_producto',)
