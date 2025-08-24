from django.db import models
from a_sucursales.models import LocalesComerciales # Necesario para la relación Cajas-LocalesComerciales
from a_empleados.models import Empleados # Necesario para la relación Cajas-Empleados

# Create your models here.
class Cajas(models.Model):
    id_cajas = models.IntegerField(db_column='ID_Cajas', primary_key=True)  # Field name made lowercase.
    # legajo_nro = models.ForeignKey('Empleados', models.DO_NOTHING, db_column='Legajo_Nro')  # Field name made lowercase.
    # id_loc_com = models.ForeignKey('LocalesComerciales', models.DO_NOTHING, db_column='ID_Loc_Com')  # Field name made lowercase.
    legajo_nro = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Legajo_Nro') # Se cambia 'Empleados' por Empleados para hacer referencia directa a la class Empleados
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com') # Se cambia 'LocalesComerciales' por LocalesComerciales para hacer referencia directa a la class LocalesComerciales
    fecha_apertura_cj = models.DateField(db_column='Fecha_Apertura_Cj', blank=True, null=True)  # Field name made lowercase.
    hora_apertura_cj = models.TimeField(db_column='Hora_Apertura_Cj', blank=True, null=True)  # Field name made lowercase.
    fecha_cierre_cj = models.DateField(db_column='Fecha_Cierre_Cj', blank=True, null=True)  # Field name made lowercase.
    hora_cierre_cj = models.TimeField(db_column='Hora_Cierre_Cj', blank=True, null=True)  # Field name made lowercase.
    monto_inicial_cj = models.DecimalField(db_column='Monto_Inicial_Cj', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    monto_final_cj = models.DecimalField(db_column='Monto_Final_Cj', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_venta_efectivo = models.DecimalField(db_column='Total_Venta_Efectivo', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_ventas_bv = models.DecimalField(db_column='Total_Ventas_BV', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_egreso_efectivo = models.DecimalField(db_column='Total_Egreso_Efectivo', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    total_egreso_bv = models.DecimalField(db_column='Total_Egreso_BV', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Cajas'

class ReportesAperturas(models.Model):
    id_ra = models.IntegerField(db_column='ID_RA', primary_key=True)  # Field name made lowercase.
    # id_cajas = models.ForeignKey('Cajas', models.DO_NOTHING, db_column='ID_Cajas')  # Field name made lowercase.
    id_cajas = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Cajas') # Se cambia 'Cajas' por Cajas para hacer referencia directa a la class Cajas
    fecha_ra = models.DateField(db_column='Fecha_RA', blank=True, null=True)  # Field name made lowercase.
    hora_ra = models.TimeField(db_column='Hora_RA', blank=True, null=True)  # Field name made lowercase.
    monto_efectivo_ra = models.DecimalField(db_column='Monto_Efectivo_RA', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    monto_bv_ra = models.DecimalField(db_column='Monto_BV_RA', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ruta_ubi_arch_ra = models.CharField(db_column='Ruta_Ubi_Arch_RA', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Reportes_Aperturas'

class ReportesCierres(models.Model):
    id_rc = models.IntegerField(db_column='ID_RC', primary_key=True)  # Field name made lowercase.
    # id_cajas = models.ForeignKey('Cajas', models.DO_NOTHING, db_column='ID_Cajas')  # Field name made lowercase.
    id_cajas = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Cajas') # Se cambia 'Cajas' por Cajas para hacer referencia directa a la class Cajas
    fecha_rc = models.DateField(db_column='Fecha_RC', blank=True, null=True)  # Field name made lowercase.
    hora_rc = models.TimeField(db_column='Hora_RC', blank=True, null=True)  # Field name made lowercase.
    monto_efectivo = models.DecimalField(db_column='Monto_Efectivo', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    monto_bv = models.DecimalField(db_column='Monto_BV', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    ruta_ubi_arch_rc = models.CharField(db_column='Ruta_Ubi_Arch_RC', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Reportes_Cierres'