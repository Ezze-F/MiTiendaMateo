from django.db import models

# Create your models here.
class Roles(models.Model):
    id_rol = models.AutoField(db_column='ID_Rol', primary_key=True)
    nombre_rol = models.CharField(db_column='Nombre_Rol', max_length=50)
    descripcion_rol = models.CharField(db_column='Descripcion_Rol', max_length=100, blank=True, null=True)
    borrado_logico = models.BooleanField(db_column='borrado_logico', default=False)

    class Meta:
        db_table = 'Roles'

    def __str__(self):
        return self.nombre_rol