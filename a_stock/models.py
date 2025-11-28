from django.db import models
# Importamos modelos desde a_central para usarlos como Foreign Keys
from a_central.models import Proveedores, Productos, LocalesComerciales


class Proveedoresxloccom(models.Model):
    id_proveedor = models.ForeignKey(Proveedores, models.DO_NOTHING, db_column='ID_Proveedor')
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com')
    
    fh_ultima_visita = models.DateTimeField(db_column='FH_Ultima_Visita', blank=True, null=True)
    borrado_pxlc = models.BooleanField(db_column='Borrado_PxLC', default=False)
    fh_borrado_pxlc = models.DateTimeField(db_column='FH_Borrado_PxLC', blank=True, null=True)

    class Meta:
        db_table = 'ProveedoresXLocCom'
        unique_together = (('id_proveedor', 'id_loc_com'),)
        verbose_name_plural = 'Proveedores por Local Comercial'
        

class Proveedoresxproductos(models.Model):
    id_prov_prod = models.AutoField(db_column='ID_Prov_Prod', primary_key=True) 
    id_proveedor = models.ForeignKey(Proveedores, models.DO_NOTHING, db_column='ID_Proveedor')
    id_producto = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Producto')
    costo_compra = models.DecimalField(db_column='Costo_Compra', max_digits=10, decimal_places=2, blank=True, null=True)
    borrado_pvxpr = models.BooleanField(db_column='Borrado_PvXPr', default=False)
    fh_borrado_pvxpr = models.DateTimeField(db_column='FH_Borrado_PvXPr', blank=True, null=True)

    class Meta:
        db_table = 'ProveedoresXProductos'
        verbose_name_plural = 'Proveedores por Productos'
        unique_together = (('id_proveedor', 'id_producto'),)
        

class Stock(models.Model):
    # Se añade PK para seguir la convención de otras tablas
    id_stock_sucursal = models.AutoField(db_column='ID_Stock_Sucursal', primary_key=True)
    id_producto = models.ForeignKey(Productos, models.DO_NOTHING, db_column='ID_Producto')
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com')
    
    stock_pxlc = models.IntegerField(db_column='Stock_PxLC')
    stock_min_pxlc = models.IntegerField(db_column='Stock_Min_PxLC')
    
    borrado_pxlc = models.BooleanField(db_column='Borrado_PxLC', default=False)
    fh_borrado_pxlc = models.DateTimeField(db_column='FH_Borrado_PxLC', blank=True, null=True)

    class Meta:
        db_table = 'Stock'
        verbose_name_plural = 'Stock por Local Comercial'
        unique_together = (('id_producto', 'id_loc_com'),)

#--------------------------------
# Modelo para observaciones de stock   
#--------------------------------

# models.py (a_stock)
from a_central.models import Proveedores, Productos, LocalesComerciales



#--------------------------------
# Modelos para lotes y vencimientos
#--------------------------------

from django.db import models
from django.utils import timezone
from a_central.models import Productos, LocalesComerciales


class LoteProducto(models.Model):
    id_lote = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE)
    id_loc_com = models.ForeignKey(LocalesComerciales, on_delete=models.CASCADE)
    numero_lote = models.CharField(max_length=30, unique=True, editable=False)
    cantidad = models.PositiveIntegerField()
    fecha_ingreso = models.DateField(default=timezone.now)
    fecha_vencimiento = models.DateField()
    activo = models.BooleanField(default=True)
    borrado_logico = models.BooleanField(default=False)  # 👈 NUEVO CAMPO

    def save(self, *args, **kwargs):
        if not self.numero_lote:
            prefix = f"P{self.id_producto.id_producto:03d}"
            fecha = timezone.now().strftime("%Y%m%d")
            cantidad_existente = LoteProducto.objects.filter(
                id_producto=self.id_producto,
                fecha_ingreso=timezone.now().date()
            ).count() + 1
            self.numero_lote = f"{prefix}-{fecha}-{cantidad_existente:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.numero_lote} - {self.id_producto.nombre_producto}"

    class Meta:
        db_table = "Lotes_Productos"
        verbose_name_plural = "Lotes de Productos"


# ---------------------------
# OBSERVACIONES DE STOCK
# ---------------------------
from django.db import models
from a_central.models import Productos
from .models import LoteProducto   # IMPORTA TU MODELO DE LOTES

class ObservacionStock(models.Model):
    producto_id = models.CharField(max_length=100)   # coincide con BD
    motivo = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateField()
    cantidad = models.PositiveIntegerField()
    lote = models.ForeignKey("LoteProducto", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.producto_id} - {self.motivo}"

