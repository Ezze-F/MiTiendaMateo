from django.db import models
from a_caja.models import Cajas # Necesario para la relación BilleterasVirtuales-Cajas

# Create your models here.
class Billeteravirtualesxcajas(models.Model):
    #pk = models.CompositePrimaryKey('ID_Cajas', 'ID_BV') Se elimina esta línea para implementar unique_together
    # id_cajas = models.ForeignKey('Cajas', models.DO_NOTHING, db_column='ID_Cajas')  # Field name made lowercase.
    id_cajas = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Cajas') # Se cambia 'Cajas' por Cajas para hacer referencia directa a la class Cajas
    id_bv = models.ForeignKey('BilleterasVirtuales', models.DO_NOTHING, db_column='ID_BV')  # Field name made lowercase.
    veces_utilizada_compra = models.IntegerField(db_column='Veces_Utilizada_Compra', blank=True, null=True)  # Field name made lowercase.
    veces_utilizada_venta = models.IntegerField(db_column='Veces_Utilizada_Venta', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'BilleteraVirtualesXCajas'
        unique_together = (('id_cajas', 'id_bv'),) # Combinación de claves para que sea única

class BilleterasVirtuales(models.Model):
    id_bv = models.IntegerField(db_column='ID_BV', primary_key=True)  # Field name made lowercase.
    # id_cajas = models.ForeignKey('Cajas', models.DO_NOTHING, db_column='ID_Cajas')  # Field name made lowercase.
    id_cajas = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Cajas') # Se cambia 'Cajas' por Cajas para hacer referencia directa a la class Cajas
    nombre_bv = models.CharField(db_column='Nombre_BV', max_length=50, blank=True, null=True)  # Field name made lowercase.
    usuario_bv = models.CharField(db_column='Usuario_BV', max_length=50, blank=True, null=True)  # Field name made lowercase.
    contrasena_bv = models.CharField(db_column='Contrasena_BV', max_length=50, blank=True, null=True)  # Field name made lowercase.
    cvu_bv = models.CharField(db_column='CVU_BV', max_length=20, blank=True, null=True)  # Field name made lowercase.
    fecha_alta_bv = models.DateField(db_column='Fecha_Alta_BV', blank=True, null=True)  # Field name made lowercase.
    hora_alta_bv = models.TimeField(db_column='Hora_Alta_BV', blank=True, null=True)  # Field name made lowercase.
    fecha_baja_bv = models.DateField(db_column='Fecha_Baja_BV', blank=True, null=True)  # Field name made lowercase.
    hora_baja_bv = models.TimeField(db_column='Hora_Baja_BV', blank=True, null=True)  # Field name made lowercase.
    saldo_bv = models.DecimalField(db_column='Saldo_BV', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Billeteras_Virtuales'