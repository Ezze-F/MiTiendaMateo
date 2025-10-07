from django.contrib import admin
from .models import Cajas, ArqueosCaja, PagosCompras, PagosVentas, MovimientosFinancieros

# Registrar y corregir CajasAdmin
@admin.register(Cajas)
class CajasAdmin(admin.ModelAdmin):
    # Corregido: Usando campos reales del modelo Cajas
    list_display = ('id_caja', 'id_loc_com', 'numero_caja', 'borrado_caja')
    list_filter = ('id_loc_com', 'borrado_caja')
    search_fields = ('id_caja', 'id_loc_com__nombre_loc_com', 'numero_caja')
    # id_loc_com es el único FK
    raw_id_fields = ('id_loc_com',)
    list_select_related = ('id_loc_com',)

# Registrar y corregir PagosComprasAdmin (Modelo PagosCompras en a_cajas/models.py)
@admin.register(PagosCompras)
class PagosComprasAdmin(admin.ModelAdmin):
    list_display = ('id_pago_compra', 'id_compra', 'id_bv', 'monto', 'fh_pago_compra', 'borrado_pc')
    list_filter = ('id_bv', 'borrado_pc')
    raw_id_fields = ('id_compra', 'id_bv',)
    list_select_related = ('id_compra', 'id_bv',)

# Registrar y corregir PagosVentasAdmin (Modelo PagosVentas en a_cajas/models.py)
@admin.register(PagosVentas)
class PagosVentasAdmin(admin.ModelAdmin):
    list_display = ('id_pago_venta', 'id_venta', 'id_bv', 'monto', 'fh_pago_venta', 'borrado_pv')
    list_filter = ('id_bv', 'borrado_pv')
    raw_id_fields = ('id_venta', 'id_bv',)
    list_select_related = ('id_venta', 'id_bv',)

# Registrar y corregir MovimientosFinancierosAdmin (Modelo MovimientosFinancieros en a_cajas/models.py)
@admin.register(MovimientosFinancieros)
class MovimientosFinancierosAdmin(admin.ModelAdmin):
    list_display = ('id_movimiento', 'tipo_movimiento', 'concepto', 'monto', 'fh_movimiento', 'borrado_movimiento')
    list_filter = ('tipo_movimiento', 'borrado_movimiento', 'id_caja', 'id_bv')
    search_fields = ('concepto',)
    raw_id_fields = ('id_caja', 'id_bv',)
    list_select_related = ('id_caja', 'id_bv',)

# Registrar y corregir ArqueosCajaAdmin (Modelo ArqueosCaja en a_cajas/models.py)
@admin.register(ArqueosCaja)
class ArqueosCajaAdmin(admin.ModelAdmin):
    list_display = ('id_arqueo', 'id_caja', 'id_empleado_apertura', 'fh_apertura', 'saldo_apertura', 'abierto_arqueo')
    list_filter = ('abierto_arqueo', 'borrado_arqueo', 'id_caja')
    search_fields = ('id_arqueo',)
    raw_id_fields = ('id_caja', 'id_empleado_apertura', 'id_empleado_cierre',)
    list_select_related = ('id_caja', 'id_empleado_apertura', 'id_empleado_cierre',)