from django.db import models
from django.utils import timezone


class Auditorias(models.Model):
    ACCION_CHOICES = [
        ('INSERT', 'INSERT'),
        ('UPDATE', 'UPDATE'),
        ('DELETE', 'DELETE'),
    ]
    id_auditoria = models.BigAutoField(primary_key=True)
    tabla_afectada = models.CharField(max_length=100)
    accion = models.CharField(max_length=6, choices=ACCION_CHOICES)
    registro_pk = models.CharField(max_length=120)
    datos_previos = models.JSONField(blank=True, null=True)
    datos_nuevos = models.JSONField(blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    legajo_empleado = models.ForeignKey('Empleados', on_delete=models.SET_NULL, db_column='legajo_empleado', blank=True, null=True)
    ip_cliente = models.CharField(max_length=64, blank=True, null=True)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Auditorias'
        verbose_name_plural = "Auditorias"


# -------------------------------------------------------------------
# Gestores de objetos personalizados para el borrado lógico.
# -------------------------------------------------------------------

class RolManager(models.Manager):
    """
    Manager que devuelve solo los roles no borrados lógicamente.
    """
    def get_queryset(self):
        return super().get_queryset().filter(borrado_logico=False)

class RolesBorradosManager(models.Manager):
    """
    Manager que devuelve solo los roles borrados lógicamente.
    """
    def get_queryset(self):
        return super().get_queryset().filter(borrado_logico=True)

# -------------------------------------------------------------------
# Modelo de Roles
# -------------------------------------------------------------------

class Roles(models.Model):
    """
    Modelo para la gestión de roles de usuario con borrado lógico.
    """
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(unique=True, max_length=50)
    descripcion_rol = models.CharField(max_length=100, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    borrado_logico = models.BooleanField(default=False)
    fecha_borrado = models.DateTimeField(null=True, blank=True)

    # Gestores de objetos
    objects = RolManager()  # El gestor por defecto, filtra los no borrados
    borrados = RolesBorradosManager()  # Un gestor para acceder a los roles borrados
    all_objects = models.Manager()  # Un gestor para acceder a todos los roles, incluyendo los borrados

    class Meta:
        db_table = 'Roles'
        verbose_name_plural = "Roles"

    def eliminacion(self):
        """
        Marca el rol como eliminado lógicamente y establece la fecha de borrado.
        """
        self.borrado_logico = True
        self.fecha_borrado = timezone.now()
        self.save()

    def restauracion(self):
        """
        Restaura un rol previamente eliminado lógicamente.
        """
        self.borrado_logico = False
        self.fecha_borrado = None
        self.save()

    def __str__(self):
        return self.nombre_rol

class Empleados(models.Model):
    legajo_nro_empleado = models.AutoField(primary_key=True)
    dni_empleado = models.CharField(unique=True, max_length=20)
    apellido_empleado = models.CharField(max_length=80)
    nombre_empleado = models.CharField(max_length=80)
    email_empleado = models.CharField(max_length=150, blank=True, null=True)
    telefono_empleado = models.CharField(max_length=30, blank=True, null=True)
    domicilio_empleado = models.CharField(max_length=200, blank=True, null=True)
    fecha_alta = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(blank=True, null=True)
    contrasena_empleado = models.CharField(max_length=255)
    id_rol = models.ForeignKey(Roles, on_delete=models.CASCADE, db_column='id_rol')
    id_sucursal = models.ForeignKey('Sucursales', on_delete=models.CASCADE, db_column='id_sucursal')
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Empleados'
        verbose_name_plural = "Empleados"

class Provincias(models.Model):
    id_provincia = models.AutoField(primary_key=True)
    nombre_provincia = models.CharField(unique=True, max_length=50)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Provincias'
        verbose_name_plural = "Provincias"

class Sucursales(models.Model):
    id_sucursal = models.AutoField(primary_key=True)
    nombre_sucursal = models.CharField(max_length=120)
    cod_postal_suc = models.CharField(max_length=10, blank=True, null=True)
    telefono_suc = models.CharField(max_length=30, blank=True, null=True)
    direccion_suc = models.CharField(max_length=200, blank=True, null=True)
    id_provincia = models.ForeignKey(Provincias, on_delete=models.CASCADE, db_column='id_provincia')
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Sucursales'
        verbose_name_plural = "Sucursales"
