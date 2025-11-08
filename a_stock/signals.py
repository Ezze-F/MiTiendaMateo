from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from .models import LoteProducto, Stock

@receiver(post_save, sender=LoteProducto)
def sincronizar_stock(sender, instance, **kwargs):
    """
    🔄 Sincroniza el stock cada vez que se crea, modifica o desactiva un lote.
    No depende de post_delete, por lo que funciona con borrado lógico (activo=False).
    """
    try:
        total_lotes_activos = LoteProducto.objects.filter(
            id_producto=instance.id_producto,
            id_loc_com=instance.id_loc_com,
            activo=True
        ).aggregate(total=models.Sum('cantidad'))['total'] or 0

        stock, _ = Stock.objects.get_or_create(
            id_producto=instance.id_producto,
            id_loc_com=instance.id_loc_com,
            defaults={'stock_pxlc': 0, 'stock_min_pxlc': 0, 'borrado_pxlc': False}
        )

        stock.stock_pxlc = total_lotes_activos
        stock.save()

        print(f"[SYNC] Stock sincronizado: {instance.id_producto.nombre_producto} → {total_lotes_activos} unidades")

    except Exception as e:
        print(f"[ERROR] Falló la sincronización de stock: {e}")
