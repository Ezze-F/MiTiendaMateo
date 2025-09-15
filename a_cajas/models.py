from django.db import models

class BilleterasVirtuales(models.Model):
    id_billetera_virtual = models.AutoField(primary_key=True)
    nombre_billetera = models.CharField(max_length=120)
    usuario_billetera = models.CharField(max_length=120, blank=True, null=True)
    contrasena_billetera = models.CharField(max_length=255, blank=True, null=True)
    cvu_billetera = models.CharField(unique=True, max_length=30, blank=True, null=True)
    saldo_billetera = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Billeteras_Virtuales'
        verbose_name_plural = "Billeteras Virtuales"

class Cajas(models.Model):
    id_caja = models.BigAutoField(primary_key=True)
    id_sucursal = models.ForeignKey('a_central.Sucursales', on_delete=models.CASCADE, db_column='id_sucursal')
    legajo_apertura_caja = models.ForeignKey('a_central.Empleados', on_delete=models.CASCADE, db_column='legajo_apertura_caja', related_name='cajas_apertura')
    legajo_cierre_caja = models.ForeignKey('a_central.Empleados', on_delete=models.SET_NULL, db_column='legajo_cierre_caja', related_name='cajas_cierre', blank=True, null=True)
    fecha_apertura = models.DateField()
    hora_apertura = models.TimeField()
    fecha_cierre = models.DateField(blank=True, null=True)
    hora_cierre = models.TimeField(blank=True, null=True)
    importe_inicial = models.DecimalField(max_digits=14, decimal_places=2, default=0.00)
    importe_final = models.DecimalField(max_digits=14, decimal_places=2, blank=True, null=True)
    abierta = models.BooleanField(default=True)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Cajas'
        verbose_name_plural = "Cajas"

class MovimientosCajas(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('APERTURA', 'APERTURA'),
        ('CIERRE', 'CIERRE'),
        ('VENTA_EFECTIVO', 'VENTA_EFECTIVO'),
        ('VENTA_BILLETERA', 'VENTA_BILLETERA'),
        ('COMPRA_EFECTIVO', 'COMPRA_EFECTIVO'),
        ('COMPRA_BILLETERA', 'COMPRA_BILLETERA'),
        ('RETIRO', 'RETIRO'),
        ('AJUSTE', 'AJUSTE'),
    ]
    id_movimiento_caja = models.BigAutoField(primary_key=True)
    id_caja = models.ForeignKey(Cajas, on_delete=models.CASCADE, db_column='id_caja')
    tipo_movimiento = models.CharField(max_length=16, choices=TIPO_MOVIMIENTO_CHOICES)
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Movimientos_Cajas'
        verbose_name_plural = "Movimientos de Cajas"