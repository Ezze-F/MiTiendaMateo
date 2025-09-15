from django.contrib import admin
from .models import BilleterasVirtuales, Cajas, MovimientosCajas

# Register your models here.

@admin.register(BilleterasVirtuales)
class BilleterasVirtualesAdmin(admin.ModelAdmin):
    list_display = ('nombre_billetera', 'cvu_billetera', 'saldo_billetera', 'fecha_alta', 'borrado_logico')
    list_filter = ('borrado_logico',)
    search_fields = ('nombre_billetera', 'cvu_billetera')

@admin.register(Cajas)
class CajasAdmin(admin.ModelAdmin):
    list_display = ('id_caja', 'id_sucursal', 'legajo_apertura_caja', 'fecha_apertura', 'hora_apertura', 'abierta')
    list_filter = ('id_sucursal', 'abierta', 'borrado_logico')
    search_fields = ('id_caja', 'id_sucursal__nombre_sucursal')
    raw_id_fields = ('id_sucursal', 'legajo_apertura_caja', 'legajo_cierre_caja',)
    list_select_related = ('id_sucursal', 'legajo_apertura_caja', 'legajo_cierre_caja',)

@admin.register(MovimientosCajas)
class MovimientosCajasAdmin(admin.ModelAdmin):
    list_display = ('id_movimiento_caja', 'id_caja', 'tipo_movimiento', 'monto', 'fecha_hora')
    list_filter = ('id_caja', 'tipo_movimiento')
    search_fields = ('id_movimiento_caja', 'descripcion')
    raw_id_fields = ('id_caja',)
    list_select_related = ('id_caja',)