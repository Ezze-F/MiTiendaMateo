from django.db import models
from a_sucursales.models import LocalesComerciales # Necesario para la relación Empleados-LocalesComerciales

# Create your models here.
class Empleados(models.Model):
    legajo_nro = models.IntegerField(db_column='Legajo_Nro', primary_key=True)  # Field name made lowercase.
    dni_emp = models.CharField(db_column='Dni_Emp', max_length=20)  # Field name made lowercase.
    apellido_emp = models.CharField(db_column='Apellido_Emp', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nombre_emp = models.CharField(db_column='Nombre_Emp', max_length=50, blank=True, null=True)  # Field name made lowercase.
    email_emp = models.CharField(db_column='Email_Emp', max_length=100, blank=True, null=True)  # Field name made lowercase.
    telefono_emp = models.CharField(db_column='Telefono_Emp', max_length=50, blank=True, null=True)  # Field name made lowercase.
    domicilio_emp = models.CharField(db_column='Domicilio_Emp', max_length=100, blank=True, null=True)  # Field name made lowercase.
    fecha_alta = models.DateTimeField(db_column='Fecha_Alta', blank=True, null=True)  # Field name made lowercase.
    fecha_baja = models.DateTimeField(db_column='Fecha_Baja', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Empleados'

class Empleadosxloccom(models.Model):
    # pk = models.CompositePrimaryKey('Legajo_Nro', 'ID_Loc_Com') Se elimina esta línea para implementar unique_together
    # legajo_nro = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Legajo_Nro')  # Field name made lowercase.
    # id_loc_com = models.ForeignKey('LocalesComerciales', models.DO_NOTHING, db_column='ID_Loc_Com')  # Field name made lowercase.
    legajo_nro = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Legajo_Nro') # Se cambia 'Empleados' por Empleados para hacer referencia directa a la class Empleados
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com') # Se cambia 'LocalesComerciales' por LocalesComerciales para hacer referencia directa a la class LocalesComerciales
    turno = models.CharField(db_column='Turno', max_length=20, blank=True, null=True)  # Field name made lowercase.
    horas_trabajadas = models.IntegerField(db_column='Horas_Trabajadas', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'EmpleadosXLocCom'
        unique_together = (('legajo_nro', 'id_loc_com'),) # Combinación de claves para que sea única

class Roles(models.Model):
    id_roles = models.IntegerField(db_column='ID_Roles', primary_key=True)  # Field name made lowercase.
    nombre_rol = models.CharField(db_column='Nombre_Rol', max_length=50, blank=True, null=True)  # Field name made lowercase.
    descripcion_rol = models.CharField(db_column='Descripcion_Rol', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Roles'

class Usuarios(models.Model):
    id_usuarios = models.IntegerField(db_column='ID_Usuarios', primary_key=True)  # Field name made lowercase.
    # legajo_nro = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='Legajo_Nro')  # Field name made lowercase.
    legajo_nro = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Legajo_Nro') # Se cambia 'Empleados' por Empleados para hacer referencia directa a la class Empleados
    contrasena = models.CharField(db_column='Contrasena', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Usuarios'

class Usuariosxloccom(models.Model):
    # pk = models.CompositePrimaryKey('ID_Usuarios', 'ID_Loc_Com') Se elimina esta línea para implementar unique_together
    # id_usuarios = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='ID_Usuarios')  # Field name made lowercase.
    # id_loc_com = models.ForeignKey('LocalesComerciales', models.DO_NOTHING, db_column='ID_Loc_Com')  # Field name made lowercase.
    id_usuarios = models.ForeignKey(Usuarios, models.DO_NOTHING, db_column='ID_Usuarios') # Se cambia 'Usuarios' por Usuarios para hacer referencia directa a la class Usuarios
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com') # Se cambia 'LocalesComerciales' por LocalesComerciales para hacer referencia directa a la class LocalesComerciales
    fecha_inicio = models.DateTimeField(db_column='Fecha_Inicio', blank=True, null=True)  # Field name made lowercase.
    observaciones = models.CharField(db_column='Observaciones', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'UsuariosXLocCom'
        unique_together = (('id_usuarios', 'id_loc_com'),) # Combinación de claves para que sea única

class Usuariosxroles(models.Model):
    # pk = models.CompositePrimaryKey('ID_Usuarios', 'ID_Roles') Se elimina esta línea para implementar unique_together
    # id_usuarios = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='ID_Usuarios')  # Field name made lowercase.
    # id_roles = models.ForeignKey('Roles', models.DO_NOTHING, db_column='ID_Roles')  # Field name made lowercase.
    id_usuarios = models.ForeignKey(Usuarios, models.DO_NOTHING, db_column='ID_Usuarios') # Se cambia 'Usuarios' por Usuarios para hacer referencia directa a la class Usuarios
    id_roles = models.ForeignKey(Roles, models.DO_NOTHING, db_column='ID_Roles') # Se cambia 'Roles' por Roles para hacer referencia directa a la class Roles
    fecha_asignacion = models.DateTimeField(db_column='Fecha_Asignacion', blank=True, null=True)  # Field name made lowercase.
    fecha_desvinculacion = models.DateTimeField(db_column='Fecha_Desvinculacion', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'UsuariosXRoles'
        unique_together = (('id_usuarios', 'id_roles'),) # Combinación de claves para que sea única