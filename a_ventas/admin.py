from django.contrib import admin
from .models import Ventas, DetallesVentas

# Register your models here.

@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    list_display = ('id_venta', 'id_sucursal', 'legajo_empleado', 'fecha_hora_venta', 'monto_total', 'situacion_venta')
    list_filter = ('id_sucursal', 'legajo_empleado', 'situacion_venta')
    search_fields = ('id_venta', 'id_sucursal__nombre_sucursal', 'legajo_empleado__apellido_empleado')
    raw_id_fields = ('id_sucursal', 'legajo_empleado', 'id_caja',)
    list_select_related = ('id_sucursal', 'legajo_empleado', 'id_caja',)

@admin.register(DetallesVentas)
class DetallesVentasAdmin(admin.ModelAdmin):
    list_display = ('id_detalle_venta', 'id_venta', 'id_producto', 'cantidad', 'precio_unitario')
    list_filter = ('id_venta', 'id_producto')
    raw_id_fields = ('id_venta', 'id_producto',)
    list_select_related = ('id_venta', 'id_producto',)