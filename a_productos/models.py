from django.db import models
from a_sucursales.models import LocalesComerciales # Necesario para la relación Productos-LocalesComerciales

# Create your models here.
class Productos(models.Model):
    id_productos = models.IntegerField(db_column='ID_Productos', primary_key=True)  # Field name made lowercase.
    nombre_producto = models.CharField(db_column='Nombre_Producto', max_length=50, blank=True, null=True)  # Field name made lowercase.
    precio_unitario = models.DecimalField(db_column='Precio_Unitario', max_digits=10, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    fecha_elaboracion = models.DateField(db_column='Fecha_Elaboracion', blank=True, null=True)  # Field name made lowercase.
    fecha_vencimiento = models.DateField(db_column='Fecha_Vencimiento', blank=True, null=True)  # Field name made lowercase.
    cant_stock = models.IntegerField(db_column='Cant_Stock', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Productos'

class Productoxloccom(models.Model):
    # pk = models.CompositePrimaryKey('ID_Productos', 'ID_Loc_Com') Se elimina esta línea para implementar unique_together
    # id_productos = models.ForeignKey('Productos', models.DO_NOTHING, db_column='ID_Productos')  # Field name made lowercase.
    # id_loc_com = models.ForeignKey('LocalesComerciales', models.DO_NOTHING, db_column='ID_Loc_Com')  # Field name made lowercase.
    id_productos = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Productos') # Se cambia 'Productos' por Productos para hacer referencia directa a la class Productos
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com') # Se cambia 'LocalesComerciales' por LocalesComerciales para hacer referencia directa a la class LocalesComerciales
    observaciones = models.CharField(db_column='Observaciones', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'ProductoXLocCom'
        unique_together = (('id_productos', 'id_loc_com'),) # Combinación de claves para que sea única

class ReportesStock(models.Model):
    id_rst = models.IntegerField(db_column='ID_RST', primary_key=True)  # Field name made lowercase.
    # id_productos = models.ForeignKey('Productos', models.DO_NOTHING, db_column='ID_Productos')  # Field name made lowercase.
    id_productos = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Productos') # Se cambia 'Productos' por Productos para hacer referencia directa a la class Productos
    fecha_rs = models.DateField(db_column='Fecha_RS', blank=True, null=True)  # Field name made lowercase.
    hora_rs = models.TimeField(db_column='Hora_RS', blank=True, null=True)  # Field name made lowercase.
    ruta_ubi_arch_rs = models.CharField(db_column='Ruta_Ubi_Arch_RS', max_length=500, blank=True, null=True)  # Field name made lowercase.
    descripcion = models.CharField(db_column='Descripcion', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Reportes_Stock'