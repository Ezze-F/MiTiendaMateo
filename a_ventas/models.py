from django.db import models
from a_caja.models import Cajas # Necesario para la realción Ventas-Cajas
from a_productos.models import Productos # Necesario para la realción Ventas-Productos

# Create your models here.
class Ventas(models.Model):
    id_ventas = models.IntegerField(db_column='ID_Ventas', primary_key=True)  # Field name made lowercase.
    # id_cajas = models.ForeignKey('Cajas', models.DO_NOTHING, db_column='ID_Cajas')  # Field name made lowercase.
    id_cajas = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Cajas') # Se cambia 'Cajas' por Cajas para hacer referencia directa a la class Cajas
    fecha_venta = models.DateField(db_column='Fecha_Venta', blank=True, null=True)  # Field name made lowercase.
    hora_venta = models.TimeField(db_column='Hora_Venta', blank=True, null=True)  # Field name made lowercase.
    monto_final = models.DecimalField(db_column='Monto_Final', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Ventas'

class DetalleVentas(models.Model):
    # pk = models.CompositePrimaryKey('ID_Ventas', 'ID_Productos') Se elimina esta línea para implementar unique_together
    # id_ventas = models.ForeignKey('Ventas', models.DO_NOTHING, db_column='ID_Ventas')  # Field name made lowercase.
    # id_productos = models.ForeignKey('Productos', models.DO_NOTHING, db_column='ID_Productos')  # Field name made lowercase.
    id_ventas = models.ForeignKey(Ventas, models.DO_NOTHING, db_column='ID_Ventas') # Se cambia 'Ventas' por Ventas para hacer referencia directa a la class Ventas
    id_productos = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Productos') # Se cambia 'Productos' por Productos para hacer referencia directa a la class Productos
    cantidad_producto = models.IntegerField(db_column='Cantidad_Producto', blank=True, null=True)  # Field name made lowercase.
    precio_unitario = models.DecimalField(db_column='Precio_Unitario', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    monto_final = models.DecimalField(db_column='Monto_Final', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Detalle_Ventas'
        unique_together = (('id_ventas', 'id_productos'),) # Combinación de claves para que sea única

class VentasCanceladas(models.Model):
    id_vc = models.IntegerField(db_column='ID_VC', primary_key=True)  # Field name made lowercase.
    # id_cajas = models.ForeignKey('Cajas', models.DO_NOTHING, db_column='ID_Cajas')  # Field name made lowercase.
    id_cajas = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Cajas') # Se cambia 'Cajas' por Cajas para hacer referencia directa a la class Cajas
    fecha_vc = models.DateField(db_column='Fecha_VC', blank=True, null=True)  # Field name made lowercase.
    hora_vc = models.TimeField(db_column='Hora_VC', blank=True, null=True)  # Field name made lowercase.
    monto_vc = models.DecimalField(db_column='Monto_VC', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Ventas_Canceladas'