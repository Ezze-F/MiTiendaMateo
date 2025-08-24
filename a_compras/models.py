from django.db import models
from a_caja.models import Cajas # Necesario para la relación Cajas-Compras de la BD
from a_sucursales.models import LocalesComerciales # Necesario para la relación  Compras-LocalesComerciales
from a_productos.models import Productos # Necesario para la relación Compras-Productos
from a_proveedores.models import Proveedores # Necesario para la relación Compras-Proveedores

# Create your models here.
class Compras(models.Model):
    id_compras = models.IntegerField(db_column='ID_Compras', primary_key=True)  # Field name made lowercase.
    # cuit_pv = models.ForeignKey('Proveedores', models.DO_NOTHING, db_column='Cuit_Pv')  # Field name made lowercase.
    # id_cajas = models.ForeignKey('Cajas', models.DO_NOTHING, db_column='ID_Cajas')  # Field name made lowercase.
    # id_loc_com = models.ForeignKey('LocalesComerciales', models.DO_NOTHING, db_column='ID_Loc_Com')  # Field name made lowercase.
    cuit_pv = models.ForeignKey(Proveedores, models.DO_NOTHING, db_column='Cuit_Pv') # Se cambia 'Proveedores' por Proveedores para hacer referencia directa a la class Proveedores
    id_cajas = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Cajas') # Se cambia 'Cajas' por Cajas para hacer referencia directa a la class Cajas
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com') # Se cambia 'LocalesComerciales' por LocalesComerciales para hacer referencia directa a la class LocalesComerciales
    fecha_com = models.DateField(db_column='Fecha_Com', blank=True, null=True)  # Field name made lowercase.
    hora_com = models.TimeField(db_column='Hora_Com', blank=True, null=True)  # Field name made lowercase.
    monto_total = models.DecimalField(db_column='Monto_Total', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ruta_arch_fact = models.CharField(db_column='Ruta_Arch_Fact', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Compras'

class ComprasCanceladas(models.Model):
    id_cc = models.IntegerField(db_column='ID_CC', primary_key=True)  # Field name made lowercase.
    # id_cajas = models.ForeignKey('Cajas', models.DO_NOTHING, db_column='ID_Cajas')  # Field name made lowercase.
    id_cajas = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Cajas') # Se cambia 'Cajas' por Cajas para hacer referencia directa a la class Cajas
    fecha_cc = models.DateField(db_column='Fecha_CC', blank=True, null=True)  # Field name made lowercase.
    hora_cc = models.TimeField(db_column='Hora_CC', blank=True, null=True)  # Field name made lowercase.
    monto_cc = models.DecimalField(db_column='Monto_CC', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Compras_Canceladas'

class DetalleCompras(models.Model):
    # pk = models.CompositePrimaryKey('ID_Compras', 'ID_Productos') Se elimina esta línea para implementar unique_together
    # id_compras = models.ForeignKey('Compras', models.DO_NOTHING, db_column='ID_Compras')  # Field name made lowercase.
    # id_productos = models.ForeignKey('Productos', models.DO_NOTHING, db_column='ID_Productos')  # Field name made lowercase.
    id_compras = models.ForeignKey(Compras, models.DO_NOTHING, db_column='ID_Compras') # Se cambia 'Compras' por Compras para hacer referencia directa a la class Compras
    id_productos = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Productos') # Se cambia 'Productos' por Productos para hacer referencia directa a la class Productos
    precio_unitario = models.DecimalField(db_column='Precio_Unitario', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    cantidad_producto = models.IntegerField(db_column='Cantidad_Producto', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Detalle_Compras'
        unique_together = (('id_compras', 'id_productos'),) # Combinación de claves para que sea única

class ReporteInconsistenciaPedidos(models.Model):
    id_rip = models.IntegerField(db_column='ID_RIP', primary_key=True)  # Field name made lowercase.
    # id_compras = models.ForeignKey('Compras', models.DO_NOTHING, db_column='ID_Compras')  # Field name made lowercase.
    id_compras = models.ForeignKey(Compras, models.DO_NOTHING, db_column='ID_Compras') # Se cambia 'Compras' por Compras para hacer referencia directa a la class Compras
    fecha_rip = models.DateField(db_column='Fecha_RIP', blank=True, null=True)  # Field name made lowercase.
    hora_rip = models.TimeField(db_column='Hora_RIP', blank=True, null=True)  # Field name made lowercase.
    ruta_ubi_arch_rip = models.CharField(db_column='Ruta_Ubi_Arch_RIP', max_length=500, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Reporte_Inconsistencia_Pedidos'