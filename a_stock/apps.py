from django.apps import AppConfig

class AStockConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'a_stock'

    def ready(self):
        import a_stock.signals
        print("[INFO] Signals de a_stock cargados correctamente ✅")
