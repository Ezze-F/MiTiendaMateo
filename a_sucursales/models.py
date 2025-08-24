from django.db import models

# Create your models here.
class Provincias(models.Model):
    id_provincias = models.IntegerField(db_column='ID_Provincias', primary_key=True)  # Field name made lowercase.
    nombre_provincia = models.CharField(db_column='Nombre_Provincia', max_length=50, blank=True, null=True)  # Field name made lowercase.
    zonageog = models.CharField(db_column='ZonaGeog', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Provincias'

class CodigosPostales(models.Model):
    id_postal = models.IntegerField(db_column='ID_Postal', primary_key=True)  # Field name made lowercase.
    # id_provincias = models.ForeignKey('Provincias', models.DO_NOTHING, db_column='ID_Provincias')  # Field name made lowercase.
    id_provincias = models.ForeignKey(Provincias, models.DO_NOTHING, db_column='ID_Provincias') # Se cambia 'Provincias' por Provincias para hacer referencia directa a la class Provincias
    localidad = models.CharField(db_column='Localidad', max_length=100, blank=True, null=True)  # Field name made lowercase.
    barrio = models.CharField(db_column='Barrio', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Codigos_Postales'

class LocalesComerciales(models.Model):
    id_loc_com = models.IntegerField(db_column='ID_Loc_Com', primary_key=True)  # Field name made lowercase.
    # id_postal = models.ForeignKey('CodigosPostales', models.DO_NOTHING, db_column='ID_Postal')  # Field name made lowercase.
    id_postal = models.ForeignKey(CodigosPostales, models.DO_NOTHING, db_column='ID_Postal') # Se cambia 'CodigosPostales' por CodigosPostales para hacer referencia directa a la class CodigosPostales
    nombre_loc_com = models.CharField(db_column='Nombre_Loc_Com', max_length=50, blank=True, null=True)  # Field name made lowercase.
    telefono_loc_com = models.CharField(db_column='Telefono_Loc_Com', max_length=20, blank=True, null=True)  # Field name made lowercase.
    email_loc_com = models.CharField(db_column='Email_Loc_Com', max_length=50, blank=True, null=True)  # Field name made lowercase.
    nombre_calle = models.CharField(db_column='Nombre_Calle', max_length=100, blank=True, null=True)  # Field name made lowercase.
    nro_calle = models.IntegerField(db_column='Nro_Calle', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        db_table = 'Locales_Comerciales'