from django.db import models
# Importamos modelos necesarios para las relaciones de Ventas
# Usamos LocalesComerciales y Empleados desde a_central
from a_central.models import LocalesComerciales, Empleados, Productos
# Usamos Cajas desde a_cajas (ya que PagosVentas en a_cajas tiene una FK a Ventas)
from a_cajas.models import Cajas


class Ventas(models.Model):

    id_venta = models.AutoField(db_column='ID_Venta', primary_key=True)
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com', verbose_name='Local Comercial')
    id_caja = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Caja', blank=True, null=True, verbose_name='Caja')
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='ID_Empleado', verbose_name='Empleado Vendedor')
    fh_venta = models.DateTimeField(db_column='FH_Venta')
    total_venta = models.DecimalField(db_column='Total_Venta', max_digits=10, decimal_places=2)
    borrado_venta = models.BooleanField(db_column='Borrado_Venta', default=False)
    fh_borrado_venta = models.DateTimeField(db_column='FH_Borrado_Venta', blank=True, null=True)

    class Meta:
        db_table = 'Ventas'
        verbose_name_plural = 'Ventas'


class DetallesVentas(models.Model):
    id_detalle_venta = models.AutoField(db_column='ID_Detalle_Venta', primary_key=True)
    # Claves foráneas a la cabecera de Venta y al Producto
    id_venta = models.ForeignKey(Ventas, models.DO_NOTHING, db_column='ID_Venta')
    id_producto = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Producto')
    cantidad = models.IntegerField(db_column='Cantidad')
    # Usamos un nombre específico para el precio en el detalle de la venta
    precio_unitario_venta = models.DecimalField(db_column='Precio_Unitario_Venta', max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(db_column='Subtotal', max_digits=10, decimal_places=2)
    borrado_det_v = models.BooleanField(db_column='Borrado_Det_V', default=False)
    fh_borrado_det_v = models.DateTimeField(db_column='FH_Borrado_Det_V', blank=True, null=True)

    class Meta:
        db_table = 'Detalles_Ventas'
        verbose_name_plural = 'Detalles de Ventas'
        # Restricción para asegurar que un producto solo se detalle una vez por venta
        unique_together = (('id_venta', 'id_producto'),)