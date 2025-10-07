from django.contrib import admin
from .models import LocalesComerciales, Empleados, Provincias, Auditorias, Marcas, Proveedores, Productos, BilleterasVirtuales, Empleadosxloccom

# ------------------ AUDITORIAS ------------------
@admin.register(Auditorias)
class AuditoriasAdmin(admin.ModelAdmin):
    # Corregido: Usando nombres de campos existentes: nombre_tabla, accion_auditoria, id_registro, fh_accion, id_usuario
    list_display = ('id_auditoria', 'nombre_tabla', 'accion_auditoria', 'id_registro', 'fh_accion', 'id_usuario')
    list_filter = ('accion_auditoria', 'nombre_tabla')
    search_fields = ('nombre_tabla', 'id_registro')
    raw_id_fields = ('id_usuario',) 

# ------------------ PROVINCIAS ------------------
@admin.register(Provincias)
class ProvinciasAdmin(admin.ModelAdmin):
    # Corregido: borrado_provincia es el nombre correcto
    list_display = ('nombre_provincia', 'borrado_provincia')
    list_filter = ('borrado_provincia',)
    search_fields = ('nombre_provincia',)

# ------------------ LOCALES COMERCIALES ------------------
@admin.register(LocalesComerciales) 
class LocalesComercialesAdmin(admin.ModelAdmin):
    # Corregido: Usando nombres de campos reales: nombre_loc_com, borrado_loc_com
    list_display = ('nombre_loc_com', 'telefono_loc_com', 'direccion_loc_com', 'id_provincia', 'borrado_loc_com')
    list_filter = ('id_provincia', 'borrado_loc_com')
    search_fields = ('nombre_loc_com', 'direccion_loc_com')
    list_select_related = ('id_provincia',)
    # raw_id_fields no es necesario si id_provincia es el único FK aquí

# ------------------ EMPLEADOS ------------------
@admin.register(Empleados)
class EmpleadosAdmin(admin.ModelAdmin):
    # Corregido: Usando nombres de campos reales: id_empleado, dni_emp, nombre_emp, apellido_emp, email_emp, borrado_emp
    list_display = ('id_empleado', 'dni_emp', 'nombre_emp', 'apellido_emp', 'email_emp', 'borrado_emp')
    list_filter = ('borrado_emp',)
    search_fields = ('id_empleado', 'dni_emp', 'apellido_emp', 'nombre_emp')
    # Eliminados raw_id_fields: 'id_rol' y 'id_sucursal' ya no existen en este modelo.

# ------------------ EMPLEADOS POR LOCAL COMERCIAL ------------------
@admin.register(Empleadosxloccom)
class EmpleadosxloccomAdmin(admin.ModelAdmin):
    list_display = ('id_empleado', 'id_loc_com', 'turno_exlc', 'horas_trabajadas')
    list_filter = ('id_loc_com', 'turno_exlc')
    raw_id_fields = ('id_empleado', 'id_loc_com',)
    list_select_related = ('id_empleado', 'id_loc_com',)

# ------------------ MARCAS ------------------
@admin.register(Marcas)
class MarcasAdmin(admin.ModelAdmin):
    list_display = ('nombre_marca', 'borrado_marca')
    list_filter = ('borrado_marca',)
    search_fields = ('nombre_marca',)

# ------------------ PROVEEDORES ------------------
@admin.register(Proveedores)
class ProveedoresAdmin(admin.ModelAdmin):
    list_display = ('cuit_prov', 'nombre_prov', 'telefono_prov', 'borrado_prov')
    list_filter = ('borrado_prov',)
    search_fields = ('cuit_prov', 'nombre_prov')

# ------------------ PRODUCTOS ------------------
@admin.register(Productos)
class ProductosAdmin(admin.ModelAdmin):
    list_display = ('id_producto', 'nombre_producto', 'id_marca', 'precio_unit_prod', 'borrado_prod')
    list_filter = ('id_marca', 'borrado_prod')
    search_fields = ('nombre_producto',)
    raw_id_fields = ('id_marca',)
    list_select_related = ('id_marca',)

# ------------------ BILLETERAS VIRTUALES ------------------
@admin.register(BilleterasVirtuales)
class BilleterasVirtualesAdmin(admin.ModelAdmin):
    list_display = ('nombre_bv', 'usuario_bv', 'cbu_bv', 'saldo_bv', 'borrado_bv')
    list_filter = ('borrado_bv',)
    search_fields = ('nombre_bv', 'usuario_bv')