from django.contrib import admin
from .models import Auditorias, Roles, Empleados, Provincias, Sucursales

# Register your models here.

@admin.register(Auditorias)
class AuditoriasAdmin(admin.ModelAdmin):
    list_display = ('tabla_afectada', 'accion', 'registro_pk', 'fecha_hora', 'legajo_empleado')
    list_filter = ('accion', 'tabla_afectada')
    search_fields = ('tabla_afectada', 'registro_pk')

@admin.register(Roles)
class RolesAdmin(admin.ModelAdmin):
    list_display = ('nombre_rol', 'descripcion_rol', 'fecha_creacion', 'borrado_logico')
    list_filter = ('borrado_logico',)
    search_fields = ('nombre_rol',)

@admin.register(Provincias)
class ProvinciasAdmin(admin.ModelAdmin):
    list_display = ('nombre_provincia', 'borrado_logico')
    list_filter = ('borrado_logico',)
    search_fields = ('nombre_provincia',)

@admin.register(Sucursales)
class SucursalesAdmin(admin.ModelAdmin):
    list_display = ('nombre_sucursal', 'telefono_suc', 'direccion_suc', 'id_provincia', 'borrado_logico')
    list_filter = ('id_provincia', 'borrado_logico')
    search_fields = ('nombre_sucursal', 'direccion_suc')
    list_select_related = ('id_provincia',) # Mejora el rendimiento para el display de id_provincia

@admin.register(Empleados)
class EmpleadosAdmin(admin.ModelAdmin):
    list_display = ('legajo_nro_empleado', 'nombre_empleado', 'apellido_empleado', 'id_rol', 'id_sucursal', 'borrado_logico')
    list_filter = ('id_rol', 'id_sucursal', 'borrado_logico')
    search_fields = ('legajo_nro_empleado', 'dni_empleado', 'apellido_empleado', 'nombre_empleado')
    list_select_related = ('id_rol', 'id_sucursal',) # Mejora el rendimiento para el display de claves foráneas
    raw_id_fields = ('id_rol', 'id_sucursal',) # Utiliza un input de texto para las claves foráneas
