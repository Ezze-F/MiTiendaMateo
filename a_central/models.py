from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User, Group

from django.db import models
from django.utils import timezone


# ===============================================
# MODELO PROVINCIAS
# ===============================================

class ProvinciaManager(models.Manager):
    """Manager que devuelve solo Provincias activas (borrado_provincia=False)."""
    def get_queryset(self):
        return super().get_queryset().filter(borrado_provincia=False)

class ProvinciaAllObjectsManager(models.Manager):
    """Manager que devuelve TODAS las Provincias (activas e inactivos)."""
    pass

class Provincias(models.Model):
    id_provincia = models.AutoField(db_column='ID_Provincia', primary_key=True)
    nombre_provincia = models.CharField(db_column='Nombre_Provincia', unique=True, max_length=50)
    
    # Control de borrado lógico
    borrado_provincia = models.BooleanField(db_column='Borrado_Provincia', default=False)
    fh_borrado_p = models.DateTimeField(db_column='FH_Borrado_P', blank=True, null=True)

    # Managers
    objects = ProvinciaManager() 
    all_objects = ProvinciaAllObjectsManager()

    class Meta:
        db_table = 'Provincias'
        verbose_name_plural = 'Provincias'

    def __str__(self):
        return self.nombre_provincia

    def borrar_logico(self):
        """Marca la provincia como borrada (borrado_provincia=True)."""
        if not self.borrado_provincia:
            self.borrado_provincia = True
            self.fh_borrado_p = timezone.now()
            self.save()
            return True
        return False

    def restaurar(self):
        """Restaura la provincia (borrado_provincia=False)."""
        if self.borrado_provincia:
            self.borrado_provincia = False
            self.fh_borrado_p = None
            self.save()
            return True
        return False

# ===============================================
# MODELO LOCALES COMERCIALES
# ===============================================

class LocalManager(models.Manager):
    """Manager que devuelve solo locales activos (borrado_loc_com=False)."""
    def get_queryset(self):
        return super().get_queryset().filter(borrado_loc_com=False)


class LocalAllObjectsManager(models.Manager):
    """Manager que devuelve TODOS los locales (activos e inactivos)."""
    pass

class LocalesComerciales(models.Model):
    id_loc_com = models.AutoField(db_column='ID_Loc_Com', primary_key=True)
    id_provincia = models.ForeignKey(Provincias, models.DO_NOTHING, db_column='ID_Provincia')
    nombre_loc_com = models.CharField(db_column='Nombre_Loc_Com', max_length=100)
    cod_postal_loc_com = models.IntegerField(db_column='Cod_Postal_Loc_Com', blank=True, null=True)
    telefono_loc_com = models.CharField(db_column='Telefono_Loc_Com', max_length=30, blank=True, null=True)
    direccion_loc_com = models.CharField(db_column='Direccion_Loc_Com', max_length=100, blank=True, null=True)
    borrado_loc_com = models.BooleanField(db_column='Borrado_Loc_Com', default=False)
    fh_borrado_lc = models.DateTimeField(db_column='FH_Borrado_LC', blank=True, null=True)
    fecha_alta_loc_com = models.DateTimeField(db_column='Fecha_Alta_Loc_Com', auto_now_add=True)

    # Managers
    objects = LocalManager()
    all_objects = LocalAllObjectsManager()

    class Meta:
        db_table = 'Locales_Comerciales'
        unique_together = (('id_provincia', 'nombre_loc_com'),)
        verbose_name_plural = 'Locales Comerciales'

    def __str__(self):
        return self.nombre_loc_com

    def borrar_logico(self):
        """Marca el local como borrado (borrado_loc_com=True)."""
        if not self.borrado_loc_com:
            self.borrado_loc_com = True
            self.fh_borrado_lc = timezone.now()
            self.save()
            return True
        return False

    def restaurar(self):
        """Restaura el local (borrado_loc_com=False)."""
        if self.borrado_loc_com:
            self.borrado_loc_com = False
            self.fh_borrado_lc = None
            self.save()
            return True
        return False


# ===============================================
# MODELO EMPLEADOS
# ===============================================

class EmpleadoManager(models.Manager):
    """Manager que devuelve solo empleados activos (borrado_emp=False)."""
    def get_queryset(self):
        # Sobrescribe el queryset base para excluir los registros borrados
        return super().get_queryset().filter(borrado_emp=False)

class EmpleadoAllObjectsManager(models.Manager):
    """Manager que devuelve TODOS los empleados (activos e inactivos)."""
    pass # No filtra nada, usa el queryset por defecto

class Empleados(models.Model):
    id_empleado = models.AutoField(db_column='ID_Empleado', primary_key=True)
    
    # ENLACE RECOMENDADO: Vinculamos al User de Django para gestión de permisos (opcional)
    user_auth = models.OneToOneField(User, on_delete=models.CASCADE, db_column='ID_User_Auth', verbose_name='Usuario del Sistema de Auth', blank=True, null=True)
    
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

    # Managers
    objects = EmpleadoManager() # Manager por defecto: solo activos
    all_objects = EmpleadoAllObjectsManager() # Manager para acceder a todos los registros

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

    def borrar_logico(self):
        """Marca el empleado como borrado (borrado_emp=True)."""
        if not self.borrado_emp:
            self.borrado_emp = True
            self.fecha_baja_emp = timezone.now().date() # Se usa date() si el campo es DateField
            self.fh_borrado_e = timezone.now()
            
            # Desactivar el usuario de Django asociado
            if self.user_auth:
                self.user_auth.is_active = False
                self.user_auth.save()
                
            self.save()
            return True
        return False # Ya estaba borrado

    def restaurar(self):
        """Restaura el empleado (borrado_emp=False)."""
        if self.borrado_emp:
            self.borrado_emp = False
            self.fecha_baja_emp = None
            self.fh_borrado_e = None
            
            # Reactivar el usuario de Django asociado
            if self.user_auth:
                self.user_auth.is_active = True
                self.user_auth.save()
                
            self.save()
            return True
        return False # Ya estaba activo


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


# ===============================================
# MODELO MARCAS
# ===============================================

class MarcaManager(models.Manager):
    """Manager que devuelve solo Marcas activas (borrado_marca=False)."""
    def get_queryset(self):
        return super().get_queryset().filter(borrado_marca=False)


class MarcaAllObjectsManager(models.Manager):
    """Manager que devuelve TODAS las Marcas (activas e inactivas)."""
    pass


class Marcas(models.Model):
    id_marca = models.AutoField(db_column='ID_Marca', primary_key=True)
    nombre_marca = models.CharField(db_column='Nombre_Marca', unique=True, max_length=50)

    # Control de borrado lógico
    borrado_marca = models.BooleanField(db_column='Borrado_Marca', default=False)
    fh_borrado_m = models.DateTimeField(db_column='FH_Borrado_M', blank=True, null=True)

    # Managers
    objects = MarcaManager()
    all_objects = MarcaAllObjectsManager()

    class Meta:
        db_table = 'Marcas'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.nombre_marca

    def borrar_logico(self):
        """Marca la marca como borrada (borrado_marca=True)."""
        if not self.borrado_marca:
            self.borrado_marca = True
            self.fh_borrado_m = timezone.now()
            self.save()
            return True
        return False

    def restaurar(self):
        """Restaura la marca (borrado_marca=False)."""
        if self.borrado_marca:
            self.borrado_marca = False
            self.fh_borrado_m = None
            self.save()
            return True
        return False


# ===============================================
# MODELO PROVEEDORES
# ===============================================

class ProveedorManager(models.Manager):
    """Manager que devuelve solo proveedores activos (borrado_prov=False)."""
    def get_queryset(self):
        return super().get_queryset().filter(borrado_prov=False)


class ProveedorAllObjectsManager(models.Manager):
    """Manager que devuelve TODOS los proveedores (activos e inactivos)."""
    pass


class Proveedores(models.Model):
    id_proveedor = models.AutoField(db_column='ID_Proveedor', primary_key=True)
    cuit_prov = models.CharField(db_column='Cuit_Prov', unique=True, max_length=15)
    nombre_prov = models.CharField(db_column='Nombre_Prov', max_length=150)
    telefono_prov = models.CharField(db_column='Telefono_Prov', max_length=20, blank=True, null=True)
    email_prov = models.CharField(db_column='Email_Prov', max_length=150, blank=True, null=True)
    direccion_prov = models.CharField(db_column='Direccion_Prov', max_length=100, blank=True, null=True)
    borrado_prov = models.BooleanField(db_column='Borrado_Prov', default=False)
    fh_borrado_prov = models.DateTimeField(db_column='FH_Borrado_Prov', blank=True, null=True)
    fecha_alta_prov = models.DateTimeField(db_column='Fecha_Alta_Prov', auto_now_add=True)
    # Managers
    objects = ProveedorManager()
    all_objects = ProveedorAllObjectsManager()

    class Meta:
        db_table = 'Proveedores'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return f'{self.nombre_prov} ({self.cuit_prov})'

    def borrar_logico(self):
        """Marca el proveedor como borrado (borrado_prov=True)."""
        if not self.borrado_prov:
            self.borrado_prov = True
            self.fh_borrado_prov = timezone.now()
            self.save()
            return True
        return False

    def restaurar(self):
        """Restaura el proveedor (borrado_prov=False)."""
        if self.borrado_prov:
            self.borrado_prov = False
            self.fh_borrado_prov = None
            self.save()
            return True
        return False

# ===============================================
# MODELO PRODUCTOS
# ===============================================

class ProductoManager(models.Manager):
    """Manager que devuelve solo productos activos (borrado_prod=False)."""
    def get_queryset(self):
        return super().get_queryset().filter(borrado_prod=False)


class ProductoAllObjectsManager(models.Manager):
    """Manager que devuelve TODOS los productos (activos e inactivos)."""
    pass

class Productos(models.Model):
    id_producto = models.AutoField(db_column='ID_Producto', primary_key=True)
    id_marca = models.ForeignKey('Marcas', models.DO_NOTHING, db_column='ID_Marca', blank=True, null=True)
    nombre_producto = models.CharField(db_column='Nombre_Producto', max_length=150, blank=True, null=True)
    precio_unit_prod = models.DecimalField(db_column='Precio_Unit_Prod', max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_venc_prod = models.DateField(db_column='Fecha_Venc_Prod', blank=True, null=True)
    borrado_prod = models.BooleanField(db_column='Borrado_Prod', default=False) 
    fh_borrado_prod = models.DateTimeField(db_column='FH_Borrado_Prod', blank=True, null=True)
    # Agregamos la fecha de alta para consistencia con DataTables/CRUD
    fecha_alta_prod = models.DateTimeField(db_column='Fecha_Alta_Prod', auto_now_add=True)

    # Managers
    objects = ProductoManager()
    all_objects = ProductoAllObjectsManager()

    class Meta:
        db_table = 'Productos'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre_producto or f"Producto {self.id_producto}"

    def borrar_logico(self):
        """Marca el producto como borrado (borrado_prod=True)."""
        if not self.borrado_prod:
            self.borrado_prod = True
            self.fh_borrado_prod = timezone.now()
            self.save()
            return True
        return False

    def restaurar(self):
        """Restaura el producto (borrado_prod=False)."""
        if self.borrado_prod:
            self.borrado_prod = False
            self.fh_borrado_prod = None
            self.save()
            return True
        return False

# ===============================================
# MODELO BILLETERAS VIRTUALES
# ===============================================

class BilleteraManager(models.Manager):
    """Manager que devuelve solo billeteras virtuales activas (borrado_bv=False)."""
    def get_queryset(self):
        return super().get_queryset().filter(borrado_bv=False)


class BilleteraAllObjectsManager(models.Manager):
    """Manager que devuelve TODAS las billeteras (activas e inactivos)."""
    pass

class BilleterasVirtuales(models.Model):
    id_bv = models.AutoField(db_column='ID_BV', primary_key=True)
    nombre_bv = models.CharField(db_column='Nombre_BV', max_length=100)
    usuario_bv = models.CharField(db_column='Usuario_BV', unique=True, max_length=100)
    # Nota: En un entorno de producción real, la contraseña NO debe guardarse como texto plano.
    # Usar el sistema de hashing de Django o un mecanismo seguro es obligatorio.
    contrasena_bv = models.CharField(db_column='Contrasena_BV', max_length=255) 
    cbu_bv = models.CharField(db_column='CBU_BV', unique=True, max_length=22, blank=True, null=True)
    fh_alta_bv = models.DateTimeField(db_column='FH_Alta_BV', default=timezone.now) # Añadimos default para manejo en Django
    fh_baja_bv = models.DateTimeField(db_column='FH_Baja_BV', blank=True, null=True)
    saldo_bv = models.DecimalField(db_column='Saldo_BV', max_digits=12, decimal_places=2, default=0.00) # Añadimos default=0.00
    borrado_bv = models.BooleanField(db_column='Borrado_BV', default=False)
    fh_borrado_bv = models.DateTimeField(db_column='FH_Borrado_BV', blank=True, null=True)

    # Managers
    objects = BilleteraManager()
    all_objects = BilleteraAllObjectsManager()

    class Meta:
        db_table = 'Billeteras_Virtuales'
        verbose_name_plural = 'Billeteras Virtuales'

    def __str__(self):
        return self.nombre_bv

    def borrar_logico(self):
        """Marca la billetera como borrada (borrado_bv=True)."""
        if not self.borrado_bv:
            self.borrado_bv = True
            self.fh_borrado_bv = timezone.now()
            # Opcional: Registrar también la fecha de baja lógica en fh_baja_bv si representa la última baja.
            self.fh_baja_bv = timezone.now() 
            self.save()
            return True
        return False

    def restaurar(self):
        """Restaura la billetera (borrado_bv=False)."""
        if self.borrado_bv:
            self.borrado_bv = False
            self.fh_borrado_bv = None
            self.save()
            return True
        return False


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