from django.contrib import admin
# Solo importamos los modelos locales de a_stock.
from .models import Proveedoresxloccom, Proveedoresxproductos, Stock
# NOTA: Los modelos Marcas, Proveedores y Productos ya no se registran aquí para evitar AlreadyRegistered

# ------------------ PROVEEDORES POR LOCAL COMERCIAL ------------------
@admin.register(Proveedoresxloccom)
class ProveedoresxloccomAdmin(admin.ModelAdmin):
    list_display = ('id_proveedor', 'id_loc_com', 'fh_ultima_visita', 'borrado_pxlc')
    list_filter = ('id_loc_com', 'borrado_pxlc')
    raw_id_fields = ('id_proveedor', 'id_loc_com',)
    list_select_related = ('id_proveedor', 'id_loc_com',)

# ------------------ PROVEEDORES POR PRODUCTOS ------------------
@admin.register(Proveedoresxproductos)
class ProveedoresxproductosAdmin(admin.ModelAdmin):
    list_display = ('id_prov_prod', 'id_proveedor', 'id_producto', 'costo_compra', 'borrado_pvxpr')
    list_filter = ('id_proveedor', 'id_producto', 'borrado_pvxpr')
    raw_id_fields = ('id_proveedor', 'id_producto',)
    list_select_related = ('id_proveedor', 'id_producto',)

# ------------------ STOCK ------------------
@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('id_stock_sucursal', 'id_producto', 'id_loc_com', 'stock_pxlc', 'stock_min_pxlc', 'borrado_pxlc')
    list_filter = ('id_loc_com', 'borrado_pxlc')
    search_fields = ('id_producto__nombre_producto', 'id_loc_com__nombre_loc_com')
    raw_id_fields = ('id_producto', 'id_loc_com',)
    list_select_related = ('id_producto', 'id_loc_com',)