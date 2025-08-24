from django.db import models
from a_sucursales.models import LocalesComerciales # Necesario para la relación Proveedores-LocalesComerciales
from a_productos.models import Productos # Necesario para la relación Proveedores-Productos

# Create your models here.
class Proveedores(models.Model):
    cuit_pv = models.IntegerField(db_column='Cuit_Pv', primary_key=True)  # Field name made lowercase.
    nombre_pv = models.CharField(db_column='Nombre_Pv', max_length=50, blank=True, null=True)  # Field name made lowercase.
    telefono_pv = models.CharField(db_column='Telefono_Pv', max_length=50, blank=True, null=True)  # Field name made lowercase.
    email_pv = models.CharField(db_column='Email_Pv', max_length=100, blank=True, null=True)  # Field name made lowercase.
    direccion_pv = models.CharField(db_column='Direccion_Pv', max_length=100, blank=True, null=True)  # Field name made lowercase.
    habilitado = models.CharField(db_column='Habilitado', max_length=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Proveedores'

class PedidosConfirmados(models.Model):
    id_pedconf = models.IntegerField(db_column='ID_PedConf', primary_key=True)  # Field name made lowercase.
    cuit_pv = models.ForeignKey('Proveedores', models.DO_NOTHING, db_column='Cuit_Pv')  # Field name made lowercase.

    class Meta:
        db_table = 'Pedidos_Confirmados'

class PedidosConfxproductos(models.Model):
    # pk = models.CompositePrimaryKey('ID_PedConf', 'ID_Productos') Se elimina esta línea para implementar unique_together
    # id_pedconf = models.ForeignKey('PedidosConfirmados', models.DO_NOTHING, db_column='ID_PedConf')  # Field name made lowercase.
    # id_productos = models.ForeignKey('Productos', models.DO_NOTHING, db_column='ID_Productos')  # Field name made lowercase.
    id_pedconf = models.ForeignKey(PedidosConfirmados, models.DO_NOTHING, db_column='ID_PedConf') # Se cambia 'PedidosConfirmados' por PedidosConfirmados para hacer referencia directa a la class PedidosConfirmados
    id_productos = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Productos') # Se cambia 'Productos' por Productos para hacer referencia directa a la class Productos
    observaciones = models.CharField(db_column='Observaciones', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Pedidos_ConfXProductos'
        unique_together = (('id_pedconf', 'id_productos'),) # Combinación de claves para que sea única

class PedidosProvisorios(models.Model):
    id_pedprov = models.IntegerField(db_column='ID_Pedprov', primary_key=True)  # Field name made lowercase.
    cantidad_prov = models.IntegerField(db_column='Cantidad_Prov', blank=True, null=True)  # Field name made lowercase.
    total_costo = models.DecimalField(db_column='Total_Costo', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Pedidos_Provisorios'

class PedidosProvxproductos(models.Model):
    # pk = models.CompositePrimaryKey('ID_Pedprov', 'ID_Productos') Se elimina esta línea para implementar unique_together
    # id_pedprov = models.ForeignKey('PedidosProvisorios', models.DO_NOTHING, db_column='ID_Pedprov')  # Field name made lowercase.
    # id_productos = models.ForeignKey('Productos', models.DO_NOTHING, db_column='ID_Productos')  # Field name made lowercase.
    id_pedprov = models.ForeignKey(PedidosProvisorios, models.DO_NOTHING, db_column='ID_Pedprov') # Se cambia 'PedidosProvisorios' por PedidosProvisorios para hacer referencia directa a la class PedidosProvisorios
    id_productos = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Productos') # Se cambia 'Productos' por Productos para hacer referencia directa a la class Productos
    descripcion = models.CharField(db_column='Descripcion', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Pedidos_ProvXProductos'
        unique_together = (('id_pedprov', 'id_productos'),) # Combinación de claves para que sea única

class Proveedoresxloccom(models.Model):
    # pk = models.CompositePrimaryKey('Cuit_Pv', 'ID_Loc_Com') Se elimina esta línea para implementar unique_together
    # cuit_pv = models.ForeignKey('Proveedores', models.DO_NOTHING, db_column='Cuit_Pv')  # Field name made lowercase.
    # id_loc_com = models.ForeignKey('LocalesComerciales', models.DO_NOTHING, db_column='ID_Loc_Com')  # Field name made lowercase.
    cuit_pv = models.ForeignKey(Proveedores, models.DO_NOTHING, db_column='Cuit_Pv') # Se cambia 'Proveedores' por Proveedores para hacer referencia directa a la class Proveedores
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com') # Se cambia 'LocalesComerciales' por LocalesComerciales para hacer referencia directa a la class LocalesComerciales
    fecha_ultima_visita = models.DateField(db_column='Fecha_Ultima_Visita', blank=True, null=True)  # Field name made lowercase.
    hora_ultima_visita = models.TimeField(db_column='Hora_Ultima_Visita', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'ProveedoresXLocCom'
        unique_together = (('cuit_pv', 'id_loc_com'),) # Combinación de claves para que sea única

class Proveedoresxproductos(models.Model):
    # pk = models.CompositePrimaryKey('Cuit_Pv', 'ID_Productos') Se elimina esta línea para implementar unique_together
    # cuit_pv = models.ForeignKey('Proveedores', models.DO_NOTHING, db_column='Cuit_Pv')  # Field name made lowercase.
    # id_productos = models.ForeignKey('Productos', models.DO_NOTHING, db_column='ID_Productos')  # Field name made lowercase.
    cuit_pv = models.ForeignKey(Proveedores, models.DO_NOTHING, db_column='Cuit_Pv') # Se cambia 'Proveedores' por Proveedores para hacer referencia directa a la class Proveedores
    id_productos = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Productos') # Se cambia 'Productos' por Productos para hacer referencia directa a la class Productos
    ultima_entrega = models.DateField(db_column='Ultima_Entrega', blank=True, null=True)  # Field name made lowercase.
    observacion = models.CharField(db_column='Observacion', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'ProveedoresXProductos'
        unique_together = (('cuit_pv', 'id_productos'),) # Combinación de claves para que sea única