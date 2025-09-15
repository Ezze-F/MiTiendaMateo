from django.contrib import admin
from .models import Marcas, Productos, Proveedores, ProveedoresProductos, StocksSucursales

# Register your models here.

@admin.register(Marcas)
class MarcasAdmin(admin.ModelAdmin):
    list_display = ('nombre_marca', 'borrado_logico')
    list_filter = ('borrado_logico',)
    search_fields = ('nombre_marca',)

@admin.register(Proveedores)
class ProveedoresAdmin(admin.ModelAdmin):
    list_display = ('cuit_proveedor', 'nombre_proveedor', 'habilitado_proveedor', 'borrado_logico')
    list_filter = ('habilitado_proveedor', 'borrado_logico')
    search_fields = ('cuit_proveedor', 'nombre_proveedor')

@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'descripcion_producto', 'id_marca', 'precio_unitario_venta', 'borrado_logico')
    list_filter = ('id_marca', 'borrado_logico')
    search_fields = ('descripcion_producto',)
    raw_id_fields = ('id_marca',)
    list_select_related = ('id_marca',)

@admin.register(ProveedoresProductos)
class ProveedoresProductosAdmin(admin.ModelAdmin):
    list_display = ('id_proveedor_producto', 'cuit_proveedor', 'id_producto', 'precio_proveedor')
    list_filter = ('cuit_proveedor', 'id_producto')
    raw_id_fields = ('cuit_proveedor', 'id_producto',)
    list_select_related = ('cuit_proveedor', 'id_producto',)

@admin.register(StocksSucursales)
class StocksSucursalesAdmin(admin.ModelAdmin):
    list_display = ('id_stock', 'id_sucursal', 'id_producto', 'cantidad_stock')
    list_filter = ('id_sucursal', 'id_producto')
    raw_id_fields = ('id_sucursal', 'id_producto',)
    list_select_related = ('id_sucursal', 'id_producto',)