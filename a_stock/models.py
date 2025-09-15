from django.db import models

class Marcas(models.Model):
    id_marca = models.AutoField(primary_key=True)
    nombre_marca = models.CharField(unique=True, max_length=120)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Marcas'
        verbose_name_plural = "Marcas"

class Proveedores(models.Model):
    cuit_proveedor = models.CharField(primary_key=True, max_length=20)
    nombre_proveedor = models.CharField(max_length=160)
    telefono_proveedor = models.CharField(max_length=30, blank=True, null=True)
    email_proveedor = models.CharField(max_length=150, blank=True, null=True)
    direccion_proveedor = models.CharField(max_length=200, blank=True, null=True)
    habilitado_proveedor = models.BooleanField(default=True)
    borrado_logico = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre_proveedor

    class Meta:
        db_table = 'Proveedores'
        verbose_name_plural = "Proveedores"

class Productos(models.Model):
    id_producto = models.BigAutoField(primary_key=True)
    id_marca = models.ForeignKey(Marcas, on_delete=models.SET_NULL, db_column='id_marca', blank=True, null=True)
    descripcion_producto = models.CharField(max_length=200)
    precio_unitario_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    fecha_elaboracion = models.DateField(blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    borrado_logico = models.BooleanField(default=False)

    def __str__(self):
        return self.descripcion_producto

    class Meta:
        db_table = 'Productos'
        verbose_name_plural = "Productos"

class ProveedoresProductos(models.Model):
    id_proveedor_producto = models.BigAutoField(primary_key=True)
    cuit_proveedor = models.ForeignKey(Proveedores, on_delete=models.CASCADE, db_column='cuit_proveedor')
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='id_producto')
    precio_proveedor = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Proveedores_Productos'
        unique_together = (('cuit_proveedor', 'id_producto'),)
        verbose_name_plural = "Proveedores de Productos"

class StocksSucursales(models.Model):
    id_stock = models.BigAutoField(primary_key=True)
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='id_producto')
    id_sucursal = models.ForeignKey('a_central.Sucursales', on_delete=models.CASCADE, db_column='id_sucursal')
    cantidad_stock = models.BigIntegerField(default=0)
    borrado_logico = models.BooleanField(default=False)

    class Meta:
        db_table = 'Stocks_Sucursales'
        unique_together = (('id_producto', 'id_sucursal'),)
        verbose_name_plural = "Stocks de Sucursales"