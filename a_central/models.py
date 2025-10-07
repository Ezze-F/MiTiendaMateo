from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group

from django.db import models
from django.utils import timezone


# ------------------ PROVINCIAS ------------------


class Provincias(models.Model):
    # Clave primaria autoincremental
    id_provincia = models.AutoField(db_column='ID_Provincia', primary_key=True)
    # Nombre de la provincia (único y con un máximo de 50 caracteres)
    nombre_provincia = models.CharField(db_column='Nombre_Provincia', unique=True, max_length=50)
    borrado_provincia = models.BooleanField(db_column='Borrado_Provincia', default=False)
    fh_borrado_p = models.DateTimeField(db_column='FH_Borrado_P', blank=True, null=True)

    class Meta:
        # Nombre de la tabla en la base de datos
        db_table = 'Provincias'
        # Nombre que se mostrará en plural en la interfaz de administración
        verbose_name_plural = 'Provincias'

    def __str__(self):
        # Representación en cadena del objeto
        return self.nombre_provincia

    def soft_delete(self):
        self.borrado_provincia = True
        self.fh_borrado_p = timezone.now()
        self.save()

    def restore(self):
        self.borrado_provincia = False
        self.fh_borrado_p = None
        self.save()


class LocalesComerciales(models.Model):
    id_loc_com = models.AutoField(db_column='ID_Loc_Com', primary_key=True)
    id_provincia = models.ForeignKey(Provincias, models.DO_NOTHING, db_column='ID_Provincia')
    nombre_loc_com = models.CharField(db_column='Nombre_Loc_Com', max_length=100)
    cod_postal_loc_com = models.IntegerField(db_column='Cod_Postal_Loc_Com', blank=True, null=True)
    telefono_loc_com = models.CharField(db_column='Telefono_Loc_Com', max_length=30, blank=True, null=True)
    direccion_loc_com = models.CharField(db_column='Direccion_Loc_Com', max_length=100, blank=True, null=True)
    borrado_loc_com = models.BooleanField(db_column='Borrado_Loc_Com', default=False) # CORREGIDO
    fh_borrado_lc = models.DateTimeField(db_column='FH_Borrado_LC', blank=True, null=True)

    class Meta:
        db_table = 'Locales_Comerciales'
        unique_together = (('id_provincia', 'nombre_loc_com'),)
        verbose_name_plural = 'Locales Comerciales'


# ------------------ EMPLEADOS ------------------

class Empleados(models.Model):
    id_empleado = models.AutoField(db_column='ID_Empleado', primary_key=True)
    
    # ENLACE RECOMENDADO: Vinculamos al User de Django para gestión de permisos (opcional)
    user_auth = models.OneToOneField(
        User, on_delete=models.CASCADE, 
        db_column='ID_User_Auth', 
        verbose_name='Usuario del Sistema de Auth', 
        blank=True, null=True
    )
    
    # Campos originales del usuario
    dni_emp = models.BigIntegerField(db_column='DNI_Emp', unique=True)
    apellido_emp = models.CharField(db_column='Apellido_Emp', max_length=80)
    nombre_emp = models.CharField(db_column='Nombre_Emp', max_length=80)
    email_emp = models.CharField(db_column='Email_Emp', unique=True, max_length=150)
    
    # Campos que se sincronizarán con el User de Django
    usuario_emp = models.CharField(db_column='Usuario_Emp', unique=True, max_length=50, blank=True, null=True)
    contrasena_emp = models.CharField(db_column='Contrasena_Emp', max_length=255) # Almacenará el hash de la contraseña

    telefono_emp = models.CharField(db_column='Telefono_Emp', max_length=20, blank=True, null=True)
    domicilio_emp = models.CharField(db_column='Domicilio_Emp', max_length=200, blank=True, null=True)
    
    fecha_alta_emp = models.DateField(db_column='Fecha_Alta_Emp')
    fecha_baja_emp = models.DateField(db_column='Fecha_Baja_Emp', blank=True, null=True)
    
    # Control de borrado lógico
    borrado_emp = models.BooleanField(db_column='Borrado_Emp', default=False)
    fh_borrado_e = models.DateTimeField(db_column='FH_Borrado_E', blank=True, null=True)

    class Meta:
        db_table = 'Empleados'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f'{self.apellido_emp}, {self.nombre_emp} ({self.dni_emp})'

    def get_rol(self):
        """Devuelve el nombre del grupo (rol) al que pertenece el empleado a través de user_auth."""
        if self.user_auth and self.user_auth.groups.exists():
            return self.user_auth.groups.first().name
        return 'Sin Rol Asignado'


class Empleadosxloccom(models.Model):
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='ID_Empleado')
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com')
    turno_exlc = models.CharField(db_column='Turno_ExLC', max_length=20)
    horas_trabajadas = models.IntegerField(db_column='Horas_Trabajadas')

    class Meta:
        db_table = 'EmpleadosXLocCom'
        # Se utiliza unique_together para forzar la unicidad de la clave compuesta
        unique_together = (('id_empleado', 'id_loc_com'),)
        verbose_name_plural = 'Empleados por Local Comercial'


class Marcas(models.Model):
    id_marca = models.AutoField(db_column='ID_Marca', primary_key=True)
    nombre_marca = models.CharField(db_column='Nombre_Marca', unique=True, max_length=50)
    borrado_marca = models.BooleanField(db_column='Borrado_Marca', default=False)
    fh_borrado_m = models.DateTimeField(db_column='FH_Borrado_M', blank=True, null=True)

    class Meta:
        db_table = 'Marcas'


class Proveedores(models.Model):
    id_proveedor = models.AutoField(db_column='ID_Proveedor', primary_key=True)
    cuit_prov = models.CharField(db_column='Cuit_Prov', unique=True, max_length=15)
    nombre_prov = models.CharField(db_column='Nombre_Prov', max_length=150)
    telefono_prov = models.CharField(db_column='Telefono_Prov', max_length=20, blank=True, null=True)
    email_prov = models.CharField(db_column='Email_Prov', max_length=150, blank=True, null=True)
    direccion_prov = models.CharField(db_column='Direccion_Prov', max_length=100, blank=True, null=True)
    borrado_prov = models.BooleanField(db_column='Borrado_Prov', default=False)
    fh_borrado_prov = models.DateTimeField(db_column='FH_Borrado_Prov', blank=True, null=True)

    class Meta:
        db_table = 'Proveedores'
        verbose_name_plural = 'Proveedores'


class Productos(models.Model):
    id_producto = models.AutoField(db_column='ID_Producto', primary_key=True)
    id_marca = models.ForeignKey('Marcas', models.DO_NOTHING, db_column='ID_Marca', blank=True, null=True)
    nombre_producto = models.CharField(db_column='Nombre_Producto', max_length=150, blank=True, null=True)
    precio_unit_prod = models.DecimalField(db_column='Precio_Unit_Prod', max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_venc_prod = models.DateField(db_column='Fecha_Venc_Prod', blank=True, null=True)
    borrado_prod = models.BooleanField(db_column='Borrado_Prod', default=False) # CORREGIDO
    fh_borrado_prod = models.DateTimeField(db_column='FH_Borrado_Prod', blank=True, null=True)

    class Meta:
        db_table = 'Productos'
        verbose_name_plural = 'Productos'


class BilleterasVirtuales(models.Model):
    id_bv = models.AutoField(db_column='ID_BV', primary_key=True)
    nombre_bv = models.CharField(db_column='Nombre_BV', max_length=100)
    usuario_bv = models.CharField(db_column='Usuario_BV', unique=True, max_length=100)
    contrasena_bv = models.CharField(db_column='Contrasena_BV', max_length=255)
    cbu_bv = models.CharField(db_column='CBU_BV', unique=True, max_length=22, blank=True, null=True)
    fh_alta_bv = models.DateTimeField(db_column='FH_Alta_BV')
    fh_baja_bv = models.DateTimeField(db_column='FH_Baja_BV', blank=True, null=True)
    saldo_bv = models.DecimalField(db_column='Saldo_BV', max_digits=12, decimal_places=2, blank=True, null=True)
    borrado_bv = models.BooleanField(db_column='Borrado_BV', default=False)
    fh_borrado_bv = models.DateTimeField(db_column='FH_Borrado_BV', blank=True, null=True)

    class Meta:
        db_table = 'Billeteras_Virtuales'
        verbose_name_plural = 'Billeteras Virtuales'


class Auditorias(models.Model):
    id_auditoria = models.AutoField(db_column='ID_Auditoria', primary_key=True)
    # Se utiliza Empleados como clave foránea, ya que está definida previamente
    id_usuario = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='ID_Usuario', blank=True, null=True)
    nombre_tabla = models.CharField(db_column='Nombre_Tabla', max_length=50)
    id_registro = models.IntegerField(db_column='ID_Registro')
    # SQL usaba ENUM, CharField es adecuado para Django
    accion_auditoria = models.CharField(db_column='Accion_Auditoria', max_length=10)
    datos_anteriores = models.JSONField(db_column='Datos_Anteriores', blank=True, null=True)
    datos_nuevos = models.JSONField(db_column='Datos_Nuevos', blank=True, null=True)
    fh_accion = models.DateTimeField(db_column='FH_Accion')

    class Meta:
        db_table = 'Auditorias'  # Nombre de tabla en la BD
        verbose_name_plural = 'Auditorias'