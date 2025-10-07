# Configuraciones de administración para la aplicación a_ventas
from django.contrib import admin
from .models import Ventas, DetallesVentas

# =================================================================
# Inline para Detalles de Venta
# Usado para mostrar los detalles al editar una Venta
# =================================================================
class DetallesVentasInline(admin.TabularInline):
    """Permite editar detalles de venta directamente en la vista de Ventas."""
    model = DetallesVentas
    extra = 1 # Número de formularios vacíos a mostrar
    # NOMBRES CORREGIDOS SEGÚN models.py: 'precio_unitario_venta' y 'subtotal'
    fields = ['id_producto', 'cantidad', 'precio_unitario_venta', 'subtotal', 'borrado_det_v']
    readonly_fields = ['subtotal'] # 'subtotal' es el cálculo de la línea (Subtotal en models.py)

# =================================================================
# Configuración para el modelo Ventas
# =================================================================
@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    """Configuración para el modelo Ventas en el panel de administración."""
    list_display = [
        'id_venta', 
        'id_loc_com',       # Sucursal (FK)
        'id_empleado',      # Empleado (FK)
        'fh_venta',         # CORREGIDO: coincide con models.py
        'total_venta',      # CORREGIDO: coincide con models.py
        'borrado_venta'     # CORREGIDO: Eliminamos 'situacion_vta' y mostramos 'borrado_venta'
    ]
    list_filter = [
        'id_loc_com', 
        'id_empleado', 
        'borrado_venta'     # CORREGIDO: Filtramos por 'borrado_venta' ya que 'situacion_vta' no existe.
    ]
    search_fields = ['id_venta', 'id_empleado__apellido', 'id_loc_com__nombre']
    
    raw_id_fields = ['id_loc_com', 'id_empleado']

    inlines = [DetallesVentasInline]

# =================================================================
# Configuración para el modelo DetallesVentas
# =================================================================
@admin.register(DetallesVentas)
class DetallesVentasAdmin(admin.ModelAdmin):
    """Configuración para el modelo DetallesVentas en el panel de administración."""
    list_display = [
        'id_detalle_venta', 
        'id_venta', 
        'id_producto', 
        'cantidad', 
        'precio_unitario_venta',  # CORREGIDO: coincide con models.py
        'subtotal'                # CORREGIDO: coincide con models.py
    ]
    list_filter = ['id_venta', 'id_producto']
    search_fields = ['id_detalle_venta', 'id_venta__id_venta']
    raw_id_fields = ['id_venta', 'id_producto']