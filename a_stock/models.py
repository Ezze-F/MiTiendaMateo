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