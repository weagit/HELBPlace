from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import json

class Canvas(models.Model):
    # Le titre de la toile
    title = models.CharField(max_length=100)

    # Dimensions de la toile (largeur et hauteur)
    width = models.PositiveIntegerField(default=25)
    height = models.PositiveIntegerField(default=25)

    # Contenu de la toile, stocké sous forme de matrice JSON
    content = models.JSONField(default=list)

    # Date de publication de la toile
    date_posted = models.DateTimeField(default=timezone.now)

    # Intervalle de temps entre chaque modification autorisée sur les pixels (en secondes)
    pixel_edit_interval = models.IntegerField(default=5)

    # Référence à l'utilisateur qui a créé cette toile
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    # Dictionnaire des timestamps de la dernière modification par chaque utilisateur
    last_edit_timestamps = models.JSONField(default=dict)

    # Dictionnaire des contributions par chaque utilisateur
    contributions = models.JSONField(default=dict)

    def __str__(self):
        """Retourne le titre de la toile"""
        return self.title

    def get_absolute_url(self):
        """Retourne l'URL de la page de détail de la toile"""
        return reverse('canvas-detail', kwargs={'pk': self.pk})

    def initialize_canvas(self):
        """
        Initialise la toile avec une matrice de pixels blancs.
        Cette méthode est appelée lors de la création de la toile pour la remplir initialement de pixels blancs.
        """
        self.content = [["#FFFFFF" for _ in range(self.width)] for _ in range(self.height)]
        self.save()

    def update_pixel(self, x, y, color, user):
        """
        Met à jour la couleur d'un pixel à une position spécifique (x, y) pour un utilisateur donné.
        Avant la mise à jour, vérifie si l'utilisateur respecte l'intervalle de temps autorisé entre les modifications.
        """
        if not self.can_user_edit(user):
            return False  # Retourne False si l'utilisateur ne respecte pas l'intervalle de modification

        if 0 <= x < self.width and 0 <= y < self.height:
            # Mise à jour de la couleur du pixel
            self.content[y][x] = color

            # Enregistrement du timestamp de la dernière modification de cet utilisateur
            self.last_edit_timestamps[str(user.id)] = timezone.now().timestamp()

            # Enregistrement de la contribution de cet utilisateur
            timestamp = timezone.now().timestamp()
            if str(user.id) in self.contributions:
                self.contributions[str(user.id)].append(timestamp)
            else:
                self.contributions[str(user.id)] = [timestamp]

            self.save()
            return True  # Retourne True si la mise à jour a été réussie
        return False  # Retourne False si les coordonnées sont invalides

    def can_user_edit(self, user):
        """
        Vérifie si un utilisateur peut modifier la toile en fonction de l'intervalle de temps entre les modifications.
        """
        last_edit_time = self.last_edit_timestamps.get(str(user.id))
        if last_edit_time:
            # Vérifie si l'utilisateur respecte l'intervalle de modification
            elapsed_time = timezone.now().timestamp() - last_edit_time
            return elapsed_time >= self.pixel_edit_interval
        return True  # Si l'utilisateur n'a jamais modifié, il peut modifier

    def get_statistics(self):
        """
        Récupère les statistiques de la toile, comme le nombre de contributions quotidiennes
        et le classement des contributeurs par nombre de modifications.
        """
        daily_contributions = {}
        top_contributors = []

        # Comptage des contributions par jour
        for user_id, timestamps in self.contributions.items():
            user = User.objects.get(id=user_id)
            for timestamp in timestamps:
                date = timezone.datetime.fromtimestamp(timestamp).date()
                if date not in daily_contributions:
                    daily_contributions[date] = 0
                daily_contributions[date] += 1

        # Trie les contributeurs par nombre de contributions
        top_contributors = sorted(
            self.contributions.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )

        # Retourne les statistiques au format attendu pour le template
        return {
            'daily_contributions': {
                'dates': list(daily_contributions.keys()),
                'counts': list(daily_contributions.values())
            },
            'top_contributors': [
                {'username': User.objects.get(id=user_id).username, 'contributions': len(contrib)}
                for user_id, contrib in top_contributors
            ]
        }
