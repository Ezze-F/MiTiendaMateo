from django.db import models
from a_central.models import Proveedores, Empleados, LocalesComerciales, Productos


class PedidosProveedor(models.Model):
    id_pedido_prov = models.AutoField(db_column='ID_Pedido_Prov', primary_key=True)
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com', verbose_name='Local Comercial')
    id_proveedor = models.ForeignKey('a_central.Proveedores', models.DO_NOTHING, db_column='ID_Proveedor')
    id_empleado = models.ForeignKey('a_central.Empleados', models.DO_NOTHING, db_column='ID_Empleado', blank=True, null=True)
    fh_pedido_prov = models.DateTimeField(db_column='FH_Pedido_Prov')
    estado_pedido_prov = models.CharField(db_column='Estado_Pedido_Prov', max_length=50)
    total_estimado = models.DecimalField(db_column='Total_Estimado', max_digits=10, decimal_places=2, blank=True, null=True)
    borrado_ped_prov = models.BooleanField(db_column='Borrado_Ped_Prov', default=False)
    fh_borrado_ped_prov = models.DateTimeField(db_column='FH_Borrado_Ped_Prov', blank=True, null=True)

    class Meta:
        db_table = 'Pedidos_Proveedor'
        verbose_name_plural = 'Pedidos a Proveedores'


class DetallePedidosProveedor(models.Model):
    id_pedido_prov = models.ForeignKey(PedidosProveedor, models.DO_NOTHING, db_column='ID_Pedido_Prov')
    id_producto = models.ForeignKey('a_central.Productos', models.DO_NOTHING, db_column='ID_Producto')
    cantidad_solicitada = models.IntegerField(db_column='Cantidad_Solicitada')
    costo_est_unit = models.DecimalField(db_column='Costo_Est_Unit', max_digits=10, decimal_places=2, blank=True, null=True)
    subtotal_est = models.DecimalField(db_column='Subtotal_Est', max_digits=10, decimal_places=2, blank=True, null=True)
    borrado_det_ped_prov = models.BooleanField(db_column='Borrado_Det_Ped_Prov', default=False)
    fh_borrado_det_ped_prov = models.DateTimeField(db_column='FH_Borrado_Det_Ped_Prov', blank=True, null=True)

    class Meta:
        db_table = 'Detalle_Pedidos_Proveedor'
        unique_together = (('id_pedido_prov', 'id_producto'),)
        verbose_name_plural = 'Detalles de Pedidos a Proveedores'


class Compras(models.Model):
    id_compra = models.AutoField(db_column='ID_Compra', primary_key=True)
    # Referencias a modelos centrales
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com', verbose_name='Local Comercial')
    cuit_proveedor = models.ForeignKey(Proveedores, models.DO_NOTHING, db_column='Cuit_Proveedor', to_field='cuit_prov')
    legajo_empleado = models.ForeignKey(Empleados, models.DO_NOTHING, db_column='Legajo_Empleado')
    
    fecha_hora_compra = models.DateTimeField(db_column='Fecha_Hora_Compra')
    monto_total = models.DecimalField(db_column='Monto_Total', max_digits=12, decimal_places=2)
    # Situación de la compra: ENUM en SQL, CharField en Django
    SITUACION_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('Completada', 'Completada'),
        ('Cancelada', 'Cancelada'),
    ]
    situacion_compra = models.CharField(
        db_column='Situacion_Compra', 
        max_length=20, 
        choices=SITUACION_CHOICES, 
        default='Completada'
    )
    borrado_compra = models.BooleanField(db_column='Borrado_Compra', default=False)
    fh_borrado_c = models.DateTimeField(db_column='FH_Borrado_C', blank=True, null=True)

    class Meta:
        db_table = 'Compras'
        verbose_name_plural = 'Compras'


class DetallesCompras(models.Model):
    id_detalle_compra = models.AutoField(db_column='ID_Detalle_Compra', primary_key=True)
    # Claves foráneas
    id_compra = models.ForeignKey(Compras, models.DO_NOTHING, db_column='ID_Compra')
    id_producto = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Producto')
    
    cantidad = models.IntegerField(db_column='Cantidad')
    precio_unitario = models.DecimalField(db_column='Precio_Unitario', max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'Detalles_Compras'
        verbose_name_plural = 'Detalles de Compras'
        # Añadimos restricción para asegurar que un producto solo se detalle una vez por compra
        unique_together = (('id_compra', 'id_producto'),)


class IncidenciasCompras(models.Model):
    id_incidencia = models.AutoField(db_column='ID_Incidencia', primary_key=True)
    id_compra = models.ForeignKey(Compras, models.DO_NOTHING, db_column='ID_Compra')
    id_producto = models.ForeignKey('a_central.Productos', models.DO_NOTHING, db_column='ID_Producto')
    tipo_problema = models.CharField(db_column='Tipo_Problema', max_length=50)
    cantidad_reportada = models.IntegerField(db_column='Cantidad_Reportada')
    descripcion_incidencia = models.TextField(db_column='Descripcion_Incidencia', blank=True, null=True)
    fh_reporte = models.DateTimeField(db_column='FH_Reporte')

    class Meta:
        db_table = 'Incidencias_Compras'
        verbose_name_plural = 'Incidencias de Compras'