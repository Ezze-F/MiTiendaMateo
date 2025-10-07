from django.db import models


class Cajas(models.Model):
    id_caja = models.AutoField(db_column='ID_Caja', primary_key=True)
    # CAMBIO TEMPORAL: añadimos null=True para permitir la migración sobre filas existentes
    id_loc_com = models.ForeignKey('a_central.LocalesComerciales', models.DO_NOTHING, db_column='ID_Loc_Com', null=True)
    # CAMBIO TEMPORAL: añadimos null=True para permitir la migración sobre filas existentes
    numero_caja = models.IntegerField(db_column='Numero_Caja', null=True)
    borrado_caja = models.BooleanField(db_column='Borrado_Caja', default=False)
    fh_borrado_caja = models.DateTimeField(db_column='FH_Borrado_Caja', blank=True, null=True)

    class Meta:
        db_table = 'Cajas'
        unique_together = (('id_loc_com', 'numero_caja'),)
        verbose_name_plural = 'Cajas'


class ArqueosCaja(models.Model):
    id_arqueo = models.AutoField(db_column='ID_Arqueo', primary_key=True)
    id_caja = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Caja')
    # Referencia a 'a_central.Empleados' y uso de related_name
    id_empleado_apertura = models.ForeignKey('a_central.Empleados', models.DO_NOTHING, db_column='ID_Empleado_Apertura', related_name='arqueos_aperturados')
    # Referencia a 'a_central.Empleados' y uso de related_name
    id_empleado_cierre = models.ForeignKey('a_central.Empleados', models.DO_NOTHING, db_column='ID_Empleado_Cierre', related_name='arqueos_cerrados', blank=True, null=True)
    fh_apertura = models.DateTimeField(db_column='FH_Apertura')
    fh_cierre = models.DateTimeField(db_column='FH_Cierre', blank=True, null=True)
    saldo_apertura = models.DecimalField(db_column='Saldo_Apertura', max_digits=12, decimal_places=2)
    saldo_cierre = models.DecimalField(db_column='Saldo_Cierre', max_digits=12, decimal_places=2, blank=True, null=True)
    monto_sistema = models.DecimalField(db_column='Monto_Sistema', max_digits=12, decimal_places=2, blank=True, null=True)
    diferencia = models.DecimalField(db_column='Diferencia', max_digits=12, decimal_places=2, blank=True, null=True)
    abierto_arqueo = models.BooleanField(db_column='Abierto_Arqueo', blank=True, null=True)
    borrado_arqueo = models.BooleanField(db_column='Borrado_Arqueo', default=False)
    fh_borrado_arqueo = models.DateTimeField(db_column='FH_Borrado_Arqueo', blank=True, null=True)

    class Meta:
        db_table = 'Arqueos_Caja'
        verbose_name_plural = 'Arqueos de Caja'


class PagosCompras(models.Model):
    id_pago_compra = models.AutoField(db_column='ID_Pago_Compra', primary_key=True)
    # Referencia a 'a_compras.Compras'
    id_compra = models.ForeignKey('a_compras.Compras', models.DO_NOTHING, db_column='ID_Compra')
    # Referencia a 'a_central.BilleterasVirtuales'
    id_bv = models.ForeignKey('a_central.BilleterasVirtuales', models.DO_NOTHING, db_column='ID_BV')
    monto = models.DecimalField(db_column='Monto', max_digits=10, decimal_places=2)
    fh_pago_compra = models.DateTimeField(db_column='FH_Pago_Compra')
    borrado_pc = models.BooleanField(db_column='Borrado_PC', default=False)
    fh_borrado_pc = models.DateTimeField(db_column='FH_Borrado_PC', blank=True, null=True)

    class Meta:
        db_table = 'Pagos_Compras'
        verbose_name_plural = 'Pagos de Compras'


class PagosVentas(models.Model):
    id_pago_venta = models.AutoField(db_column='ID_Pago_Venta', primary_key=True)
    # Referencia a 'a_ventas.Ventas'
    id_venta = models.ForeignKey('a_ventas.Ventas', models.DO_NOTHING, db_column='ID_Venta')
    # Referencia a 'a_central.BilleterasVirtuales'
    id_bv = models.ForeignKey('a_central.BilleterasVirtuales', models.DO_NOTHING, db_column='ID_BV')
    monto = models.DecimalField(db_column='Monto', max_digits=10, decimal_places=2)
    fh_pago_venta = models.DateTimeField(db_column='FH_Pago_Venta')
    borrado_pv = models.BooleanField(db_column='Borrado_PV', default=False)
    fh_borrado_pv = models.DateTimeField(db_column='FH_Borrado_PV', blank=True, null=True)

    class Meta:
        db_table = 'Pagos_Ventas'
        verbose_name_plural = 'Pagos de Ventas'


class MovimientosFinancieros(models.Model):
    id_movimiento = models.AutoField(db_column='ID_Movimiento', primary_key=True)
    id_caja = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Caja', blank=True, null=True)
    # Referencia a 'a_central.BilleterasVirtuales'
    id_bv = models.ForeignKey('a_central.BilleterasVirtuales', models.DO_NOTHING, db_column='ID_BV', blank=True, null=True)
    tipo_movimiento = models.CharField(db_column='Tipo_Movimiento', max_length=20)
    concepto = models.CharField(db_column='Concepto', max_length=200)
    monto = models.DecimalField(db_column='Monto', max_digits=12, decimal_places=2)
    fh_movimiento = models.DateTimeField(db_column='FH_Movimiento')
    borrado_movimiento = models.BooleanField(db_column='Borrado_Movimiento', default=False)
    fh_borrado_movimiento = models.DateTimeField(db_column='FH_Borrado_Movimiento', blank=True, null=True)

    class Meta:
        db_table = 'Movimientos_Financieros'
        verbose_name_plural = 'Movimientos Financieros'