from django.db import models
from django.utils import timezone

# NOTA: Se asume que LocalesComerciales existe y se importa correctamente desde a_central.models
# Para la ejecución independiente, es fundamental que esta importación funcione o que definas el modelo aquí.
try:
    from a_central.models import LocalesComerciales
except ImportError:
    # MOCKUP: Si no puedes importar, usa un modelo temporal (recuerda migrarlo si es necesario)
    class LocalesComerciales(models.Model):
        id_loc_com = models.AutoField(primary_key=True)
        nombre_loc_com = models.CharField(max_length=100)
        class Meta:
            app_label = 'a_cajas' # Debe coincidir con la app
            managed = False # Si existe en otra DB/App, usar Managed=False
            db_table = 'Locales_Comerciales'

# ===============================================
# MODELO CAJAS
# ===============================================

class CajaManager(models.Manager):
    """Manager que devuelve solo cajas activas (borrado_caja=False)."""
    def get_queryset(self):
        return super().get_queryset().filter(borrado_caja=False)

class CajaAllObjectsManager(models.Manager):
    """Manager que devuelve TODAS las cajas (activas e inactivos)."""
    def get_queryset(self):
        return super().get_queryset()

class Cajas(models.Model):
    id_caja = models.AutoField(db_column='ID_Caja', primary_key=True)
    id_loc_com = models.ForeignKey(LocalesComerciales, models.DO_NOTHING, db_column='ID_Loc_Com', null=True)
    numero_caja = models.IntegerField(db_column='Numero_Caja', null=True)
    
    # NUEVO CAMPO: Estado de la caja
    caja_abierta = models.BooleanField(db_column='Caja_Abierta', default=False, 
                                       help_text="Indica si la caja está actualmente abierta para transacciones.")
    
    borrado_caja = models.BooleanField(db_column='Borrado_Caja', default=False)
    fh_borrado_caja = models.DateTimeField(db_column='FH_Borrado_Caja', blank=True, null=True)
    fh_alta_caja = models.DateTimeField(db_column='FH_Alta_Caja', default=timezone.now)

    # Managers
    objects = CajaManager()
    all_objects = CajaAllObjectsManager()

    class Meta:
        db_table = 'Cajas'
        unique_together = (('id_loc_com', 'numero_caja'),)
        verbose_name_plural = 'Cajas'

    def __str__(self):
        local_nombre = self.id_loc_com.nombre_loc_com if self.id_loc_com else 'Sin Local'
        estado = "Abierta" if self.caja_abierta else "Cerrada" 
        return f"Caja N°{self.numero_caja} en {local_nombre} ({estado})"

    def abrir(self):
        """Abre la caja si está cerrada y no borrada."""
        if not self.caja_abierta and not self.borrado_caja:
            self.caja_abierta = True
            self.save()
            return True
        return False

    def cerrar(self):
        """Cierra la caja si está abierta y no borrada."""
        if self.caja_abierta and not self.borrado_caja:
            self.caja_abierta = False
            self.save()
            return True
        return False
    
    def borrar_logico(self):
        """Marca la caja como borrada (borrado_caja=True), solo si está cerrada."""
        if not self.borrado_caja and not self.caja_abierta: # Corregido: usa caja_abierta
            self.borrado_caja = True
            self.fh_borrado_caja = timezone.now()
            self.save()
            return True
        return False 
    
    def restaurar(self):
        """Restaura la caja (borrado_caja=False)."""
        if self.borrado_caja:
            self.borrado_caja = False
            self.fh_borrado_caja = None
            self.save()
            return True
        return False

class ArqueoCaja(models.Model):
    id_arqueo = models.AutoField(db_column='ID_Arqueo', primary_key=True)
    id_caja = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Caja')
    
    # ----------------------------------------------
    # Datos de Apertura
    # ----------------------------------------------
    fh_apertura = models.DateTimeField(db_column='FH_Apertura', default=timezone.now)
    # Monto de efectivo con el que se inicia el ciclo (conteo físico)
    monto_inicial_efectivo = models.DecimalField(db_column='Monto_Inicial_Efectivo', max_digits=12, decimal_places=2) 
    # El empleado que abre la caja
    id_empleado_apertura = models.ForeignKey('a_central.Empleados', models.DO_NOTHING, db_column='ID_Empleado_Apertura', related_name='arqueos_abiertos') 
    
    # ----------------------------------------------
    # Datos de Cierre (se llenan al cerrar)
    # ----------------------------------------------
    fh_cierre = models.DateTimeField(db_column='FH_Cierre', blank=True, null=True)
    # Monto de efectivo con el que se cierra el ciclo (conteo físico)
    monto_final_efectivo = models.DecimalField(db_column='Monto_Final_Efectivo', max_digits=12, decimal_places=2, blank=True, null=True) 
    # El empleado que cierra la caja
    id_empleado_cierre = models.ForeignKey('a_central.Empleados', models.DO_NOTHING, db_column='ID_Empleado_Cierre', related_name='arqueos_cerrados', blank=True, null=True) 
    
    # ----------------------------------------------
    # Cálculos y Totales (Calculados al momento del cierre)
    # ----------------------------------------------
    # Suma de todos los movimientos de INGRESO en efectivo (desde MovimientosFinancieros)
    total_ingresos_efectivo_calculado = models.DecimalField(db_column='Total_Ingresos_Efectivo_Calculado', max_digits=12, decimal_places=2, default=0) 
    # Suma de todos los movimientos de EGRESO en efectivo (desde MovimientosFinancieros)
    total_egresos_efectivo_calculado = models.DecimalField(db_column='Total_Egresos_Efectivo_Calculado', max_digits=12, decimal_places=2, default=0) 
    
    # TOTALES DE BILLETERAS VIRTUALES (Lo que pides)
    total_ingresos_bv = models.DecimalField(db_column='Total_Ingresos_BV', max_digits=12, decimal_places=2, default=0)
    total_egresos_bv = models.DecimalField(db_column='Total_Egresos_BV', max_digits=12, decimal_places=2, default=0)
    
    # ----------------------------------------------
    # Resultados del Arqueo
    # ----------------------------------------------
    # Sobrante (positivo) o Faltante (negativo)
    diferencia_arqueo = models.DecimalField(db_column='Diferencia_Arqueo', max_digits=12, decimal_places=2, blank=True, null=True) 
    observaciones = models.TextField(db_column='Observaciones', blank=True, null=True)
    
    # Estado para saber si el ciclo de caja ya está cerrado y arqueado
    cerrado = models.BooleanField(db_column='Cerrado', default=False)
    
    class Meta:
        db_table = 'Arqueo_Caja'
        verbose_name_plural = 'Arqueos de Caja'


class MovimientosFinancieros(models.Model):
    id_movimiento = models.AutoField(db_column='ID_Movimiento', primary_key=True)
    
    # Relación Clave: Indica a qué ciclo de caja pertenece este movimiento
    # Un movimiento siempre ocurre dentro de un ArqueoCaja si es un movimiento de caja.
    id_arqueo = models.ForeignKey(ArqueoCaja, models.DO_NOTHING, db_column='ID_Arqueo', blank=True, null=True) 

    # id_caja se vuelve redundante si usamos id_arqueo, pero se puede mantener por si el movimiento no es de caja.
    # id_caja = models.ForeignKey(Cajas, models.DO_NOTHING, db_column='ID_Caja', blank=True, null=True) 
    
    id_bv = models.ForeignKey('a_central.BilleterasVirtuales', models.DO_NOTHING, db_column='ID_BV', blank=True, null=True)
    id_compra = models.ForeignKey('a_compras.Compras', models.DO_NOTHING, db_column='ID_Compra', null=True, blank=True)
    id_venta = models.ForeignKey('a_ventas.Ventas', models.DO_NOTHING, db_column='ID_Venta', null=True, blank=True)

    # IMPORTANTE: Definir si el movimiento es en EFECTIVO o BILLETERA VIRTUAL
    medio_pago = models.CharField(db_column='Medio_Pago', max_length=20) # E.g., 'EFECTIVO', 'BV'
    
    tipo_movimiento = models.CharField(db_column='Tipo_Movimiento', max_length=20) # E.g., 'INGRESO', 'EGRESO', 'VENTA', 'RETIRO'
    concepto = models.CharField(db_column='Concepto', max_length=200)
    monto = models.DecimalField(db_column='Monto', max_digits=12, decimal_places=2)
    fh_movimiento = models.DateTimeField(db_column='FH_Movimiento', default=timezone.now) 
    borrado_movimiento = models.BooleanField(db_column='Borrado_Movimiento', default=False)
    fh_borrado_movimiento = models.DateTimeField(db_column='FH_Borrado_Movimiento', blank=True, null=True)

    class Meta:
        db_table = 'Movimientos_Financieros'
        verbose_name_plural = 'Movimientos Financieros'

class PagosCompras(models.Model):
    id_pago_compra = models.AutoField(db_column='ID_Pago_Compra', primary_key=True)
    # Referencia a 'a_compras.Compras'
    id_compra = models.ForeignKey('a_compras.Compras', models.DO_NOTHING, db_column='ID_Compra')
    # Referencia a 'a_central.BilleterasVirtuales'
    id_bv = models.ForeignKey('a_central.BilleterasVirtuales', models.DO_NOTHING, db_column='ID_BV')
    monto = models.DecimalField(db_column='Monto', max_digits=10, decimal_places=2)
    fh_pago_compra = models.DateTimeField(db_column='FH_Pago_Compra', default=timezone.now)
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
    fh_pago_venta = models.DateTimeField(db_column='FH_Pago_Venta', default=timezone.now)
    borrado_pv = models.BooleanField(db_column='Borrado_PV', default=False)
    fh_borrado_pv = models.DateTimeField(db_column='FH_Borrado_PV', blank=True, null=True)

    class Meta:
        db_table = 'Pagos_Ventas'
        verbose_name_plural = 'Pagos de Ventas'