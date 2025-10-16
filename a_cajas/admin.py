from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Cajas, ArqueoCaja, PagosCompras, PagosVentas, MovimientosFinancieros

# Registrar y corregir CajasAdmin
@admin.register(Cajas)
class CajasAdmin(admin.ModelAdmin):
    list_display = ('id_caja', 'id_loc_com', 'numero_caja', 'caja_abierta', 'borrado_caja')
    list_filter = ('id_loc_com', 'caja_abierta', 'borrado_caja')
    search_fields = ('id_caja', 'id_loc_com__nombre_loc_com', 'numero_caja')
    raw_id_fields = ('id_loc_com',)
    list_select_related = ('id_loc_com',)

# Registrar y corregir PagosComprasAdmin 
@admin.register(PagosCompras)
class PagosComprasAdmin(admin.ModelAdmin):
    list_display = ('id_pago_compra', 'id_compra', 'id_bv', 'monto', 'fh_pago_compra', 'borrado_pc')
    list_filter = ('id_bv', 'borrado_pc')
    raw_id_fields = ('id_compra', 'id_bv',)
    list_select_related = ('id_compra', 'id_bv',)

# Registrar y corregir PagosVentasAdmin 
@admin.register(PagosVentas)
class PagosVentasAdmin(admin.ModelAdmin):
    list_display = ('id_pago_venta', 'id_venta', 'id_bv', 'monto', 'fh_pago_venta', 'borrado_pv')
    list_filter = ('id_bv', 'borrado_pv')
    raw_id_fields = ('id_venta', 'id_bv',)
    list_select_related = ('id_venta', 'id_bv',)

# Registrar y corregir MovimientosFinancierosAdmin 
@admin.register(MovimientosFinancieros)
class MovimientosFinancierosAdmin(admin.ModelAdmin):
    # Corregido: El FK que apunta al ciclo de caja es 'id_arqueo', NO 'id_caja'.
    list_display = ('id_movimiento', 'id_arqueo', 'tipo_movimiento', 'concepto', 'monto', 'fh_movimiento', 'borrado_movimiento')
    list_filter = ('tipo_movimiento', 'borrado_movimiento', 'id_arqueo', 'id_bv') # Usamos id_arqueo
    search_fields = ('concepto',)
    raw_id_fields = ('id_arqueo', 'id_bv',) # Usamos id_arqueo
    # 'id_arqueo' reemplaza a 'id_caja'
    list_select_related = ('id_arqueo', 'id_bv',) 


# Registrar y corregir ArqueosCajaAdmin 
@admin.register(ArqueoCaja)
class ArqueosCajaAdmin(admin.ModelAdmin):
    # Correcciones en list_display: 
    # 1. 'saldo_apertura' -> Reemplazado por el método 'get_monto_inicial'.
    # 2. 'abierto_arqueo' -> Reemplazado por el método 'es_abierto'.
    list_display = ('id_arqueo', 'id_caja', 'id_empleado_apertura', 'fh_apertura', 'get_monto_inicial', 'es_abierto')
    
    # Correcciones en list_filter: 
    # 1. 'abierto_arqueo' -> Reemplazado por el campo real 'cerrado' (usado como negación).
    # 2. 'borrado_arqueo' -> El modelo ArqueoCaja NO tiene 'borrado_arqueo', así que lo quitamos.
    list_filter = ('cerrado', 'id_caja__id_loc_com', 'id_caja')
    
    search_fields = ('id_arqueo',)
    raw_id_fields = ('id_caja', 'id_empleado_apertura', 'id_empleado_cierre',)
    list_select_related = ('id_caja', 'id_empleado_apertura', 'id_empleado_cierre',)

    # ====================================================================
    # Métodos para list_display que reemplazan campos inexistentes
    # ====================================================================

    @admin.display(description='Monto Inicial')
    def get_monto_inicial(self, obj):
        """Muestra el monto inicial formateado y coloreado (reemplaza saldo_apertura)."""
        if obj.monto_inicial_efectivo is not None:
            # Puedes usar una función de formato de moneda si tienes una definida, 
            # pero por simplicidad usaremos un formato básico.
            monto = f"${obj.monto_inicial_efectivo:,.2f}"
            return mark_safe(f'<span style="font-weight: bold;">{monto}</span>')
        return "N/A"
    
    @admin.display(boolean=True, description='Abierto')
    def es_abierto(self, obj):
        """Indica si el arqueo está abierto (NO cerrado). Reemplaza abierto_arqueo."""
        # Si el campo 'cerrado' es False, significa que está Abierto.
        return not obj.cerrado 
