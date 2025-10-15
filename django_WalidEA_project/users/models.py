from django.db import models
from django.contrib.auth.models import User
from PIL import Image

class Profile(models.Model):
    # Définition de la relation entre le modèle Profile et User (un utilisateur peut avoir un profil)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Champ pour l'image de profil, avec une valeur par défaut
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')

    # Représentation sous forme de chaîne du profil, affichant le nom de l'utilisateur
    def __str__(self):
        return f'{self.user.username} Profile'

    # Méthode pour sauvegarder l'image de profil
    def save(self, *args, **kwargs):
        # Sauvegarde de l'instance avant toute modification
        super(Profile, self).save(*args, **kwargs)

        # Ouvrir l'image à l'aide de la bibliothèque PIL
        img = Image.open(self.image.path)

        # Si l'image est trop grande (plus de 300x300 pixels), on la redimensionne
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)  # Taille cible
            img.thumbnail(output_size)  # Redimensionner l'image en maintenant le ratio
            img.save(self.image.path)   # Sauvegarder l'image redimensionnée
