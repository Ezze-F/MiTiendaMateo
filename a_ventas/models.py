from django.db import models
from django.utils import timezone
from a_central.models import LocalesComerciales, Empleados, Productos
from a_cajas.models import Cajas

class Ventas(models.Model):
    id_venta = models.AutoField(db_column='ID_Venta', primary_key=True)
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com', verbose_name='Local Comercial')
    id_caja = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Caja', blank=True, null=True, verbose_name='Caja')
    id_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='ID_Empleado', verbose_name='Empleado Vendedor')
    fh_venta = models.DateTimeField(db_column='FH_Venta', default=timezone.now)
    total_venta = models.DecimalField(db_column='Total_Venta', max_digits=10, decimal_places=2, default=0)
    borrado_venta = models.BooleanField(db_column='Borrado_Venta', default=False)
    fh_borrado_venta = models.DateTimeField(db_column='FH_Borrado_Venta', blank=True, null=True)

    class Meta:
        db_table = 'Ventas'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f"Venta {self.id_venta} - ${self.total_venta}"

class DetallesVentas(models.Model):
    id_detalle_venta = models.AutoField(db_column='ID_Detalle_Venta', primary_key=True)
    id_venta = models.ForeignKey(Ventas, models.DO_NOTHING, db_column='ID_Venta', related_name='detalles')
    id_producto = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Producto')
    cantidad = models.IntegerField(db_column='Cantidad')
    precio_unitario_venta = models.DecimalField(db_column='Precio_Unitario_Venta', max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(db_column='Subtotal', max_digits=10, decimal_places=2)
    borrado_det_v = models.BooleanField(db_column='Borrado_Det_V', default=False)
    fh_borrado_det_v = models.DateTimeField(db_column='FH_Borrado_Det_V', blank=True, null=True)

    class Meta:
        db_table = 'Detalles_Ventas'
        verbose_name_plural = 'Detalles de Ventas'
        unique_together = (('id_venta', 'id_producto'),)

    def save(self, *args, **kwargs):
        # Calcular automáticamente el subtotal
        self.subtotal = self.cantidad * self.precio_unitario_venta
        super().save(*args, **kwargs)