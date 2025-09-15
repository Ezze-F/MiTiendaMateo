from django.db import models

class Ventas(models.Model):
    SITUACION_VENTA_CHOICES = [
        ('FINALIZADO', 'FINALIZADO'),
        ('EN_PROCESO', 'EN_PROCESO'),
        ('CANCELADO', 'CANCELADO'),
    ]
    id_venta = models.BigAutoField(primary_key=True)
    id_sucursal = models.ForeignKey('a_central.Sucursales', on_delete=models.CASCADE, db_column='id_sucursal')
    legajo_empleado = models.ForeignKey('a_central.Empleados', on_delete=models.CASCADE, db_column='legajo_empleado')
    id_caja = models.ForeignKey('a_cajas.Cajas', on_delete=models.CASCADE, db_column='id_caja')
    fecha_hora_venta = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    situacion_venta = models.CharField(max_length=10, choices=SITUACION_VENTA_CHOICES)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Ventas'
        verbose_name_plural = "Ventas"

class DetallesVentas(models.Model):
    id_detalle_venta = models.BigAutoField(primary_key=True)
    id_venta = models.ForeignKey('Ventas', on_delete=models.CASCADE, db_column='id_venta')
    id_producto = models.ForeignKey('a_stock.Productos', on_delete=models.CASCADE, db_column='id_producto')
    cantidad = models.BigIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Detalles_Ventas'
        unique_together = (('id_venta', 'id_producto'),)
        verbose_name_plural = "Detalles de Ventas"