from django.db.models.signals import post_save  # Importation du signal 'post_save'
from django.contrib.auth.models import User  # Importation du modèle User
from django.dispatch import receiver  # Importation du décorateur 'receiver'
from .models import Profile  # Importation du modèle Profile

# Signal déclenché après la création d'un utilisateur
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Cette fonction crée automatiquement un profil lorsqu'un utilisateur est créé.
    Elle est appelée dès qu'un nouvel utilisateur est enregistré dans la base de données.
    """
    if created:
        Profile.objects.create(user=instance)  # Crée un profil pour l'utilisateur

# Signal déclenché après la sauvegarde d'un utilisateur
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Cette fonction enregistre le profil de l'utilisateur chaque fois qu'il est sauvegardé.
    Elle est appelée chaque fois qu'un utilisateur est modifié (après un post_save).
    """
    instance.profile.save()  # Sauvegarde le profil de l'utilisateur
