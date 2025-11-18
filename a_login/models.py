# a_login/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    """
    Modelo de perfil para extender el User de Django, 
    utilizado para almacenar información de seguridad y control de intentos de login.
    """
    # Relación uno a uno con el usuario estándar de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Campos para el control de seguridad
    # Contador de intentos fallidos
    login_attempts = models.IntegerField(default=0)
    # Momento del último intento fallido
    last_login_fail = models.DateTimeField(null=True, blank=True) 
    # Momento en que el bloqueo debe terminar (para el bloqueo de 10 minutos)
    unlock_time = models.DateTimeField(null=True, blank=True) 

    # Propiedad para verificar si el usuario está bloqueado
    @property
    def is_locked(self):
        """Devuelve True si el tiempo actual es anterior al tiempo de desbloqueo."""
        # Compara el tiempo actual (timezone.now()) con el tiempo de desbloqueo futuro.
        return self.unlock_time and timezone.now() < self.unlock_time

    def __str__(self):
        return self.user.username

# a_login/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class UserProfile(models.Model):
    """
    Modelo de perfil para extender el User de Django, 
    utilizado para almacenar información de seguridad y control de intentos de login.
    """
    # Relación uno a uno con el usuario estándar de Django
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Campos para el control de seguridad
    # Contador de intentos fallidos
    login_attempts = models.IntegerField(default=0)
    # Momento del último intento fallido
    last_login_fail = models.DateTimeField(null=True, blank=True) 
    # Momento en que el bloqueo debe terminar (para el bloqueo de 10 minutos)
    unlock_time = models.DateTimeField(null=True, blank=True) 

    # Propiedad para verificar si el usuario está bloqueado
    @property
    def is_locked(self):
        """Devuelve True si el tiempo actual es anterior al tiempo de desbloqueo."""
        # Compara el tiempo actual (timezone.now()) con el tiempo de desbloqueo futuro.
        return self.unlock_time and timezone.now() < self.unlock_time

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Crea un UserProfile cuando se crea un nuevo User."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Asegura que el UserProfile se guarde cuando el User se guarda."""
    try:
        instance.userprofile.save()
    except UserProfile.DoesNotExist:
        # Esto manejará el caso si un usuario fue creado antes de que las señales estuvieran activas
        UserProfile.objects.create(user=instance)