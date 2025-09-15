from django.db import models

class Compras(models.Model):
    SITUACION_COMPRA_CHOICES = [
        ('FINALIZADO', 'FINALIZADO'),
        ('EN_PROCESO', 'EN_PROCESO'),
        ('CANCELADO', 'CANCELADO'),
    ]
    id_compra = models.BigAutoField(primary_key=True)
    id_sucursal = models.ForeignKey('a_central.Sucursales', on_delete=models.CASCADE, db_column='id_sucursal')
    cuit_proveedor = models.ForeignKey('a_stock.Proveedores', on_delete=models.CASCADE, db_column='cuit_proveedor')
    legajo_empleado = models.ForeignKey('a_central.Empleados', on_delete=models.CASCADE, db_column='legajo_empleado')
    fecha_hora_compra = models.DateTimeField(auto_now_add=True)
    monto_total = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    situacion_compra = models.CharField(max_length=10, choices=SITUACION_COMPRA_CHOICES)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Compras'
        verbose_name_plural = "Compras"

class DetallesCompras(models.Model):
    id_detalle_compra = models.BigAutoField(primary_key=True)
    id_compra = models.ForeignKey(Compras, on_delete=models.CASCADE, db_column='id_compra')
    id_producto = models.ForeignKey('a_stock.Productos', on_delete=models.CASCADE, db_column='id_producto')
    cantidad = models.BigIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Detalles_Compras'
        unique_together = (('id_compra', 'id_producto'),)
        verbose_name_plural = "Detalles de Compras"