from django.urls import path
from .views import (
    CanvasListView,         # Vue pour afficher la liste des canvases
    CanvasDetailView,       # Vue pour afficher les détails d'un canvas
    CanvasCreateView,       # Vue pour créer un nouveau canvas
    CanvasDeleteView,       # Vue pour supprimer un canvas
    update_pixel,           # Vue pour modifier un pixel spécifique
    get_canvas_data,        # Vue pour récupérer les données d'un canvas
)
from . import views  # Import de la vue 'community' et autres fonctions

# Liste des URLS utilisées dans le blog pour gérer les canvases et leurs interactions
urlpatterns = [
    # Affichage de la liste de tous les canvases (page d'accueil)
    path('', CanvasListView.as_view(), name='canvas-home'),
    
    # Détail d'un canvas spécifique, avec son ID dans l'URL
    path('canvas/<int:pk>/', CanvasDetailView.as_view(), name='canvas-detail'),
    
    # Création d'un nouveau canvas
    path('canvas/new/', CanvasCreateView.as_view(), name='canvas-create'),
    
    # Mise à jour d'un canvas spécifique en utilisant son ID
    
    # Suppression d'un canvas spécifique
    path('canvas/<int:pk>/delete/', CanvasDeleteView.as_view(), name='canvas-delete'),
    
    # API pour la mise à jour d'un pixel d'un canvas spécifique via une requête POST
    path('api/canvas/<int:pk>/update_pixel/', update_pixel, name='update-pixel'),
    
    # API pour récupérer les données d'un canvas spécifique, utilisé pour les mises à jour en temps réel
    path('api/canvas/<int:pk>/get_data/', get_canvas_data, name='get-canvas-data'),
    
    # Page "Community" où les utilisateurs interagissent avec une toile commune
    path('community/', views.community, name='blog-community'),
    
    # Mise à jour d'un pixel pour la communauté (interactions avec la toile B2)
    path('community/update_pixel/', views.updatePixelCommunity, name='update_pixel_community'),
    
    # Statistiques détaillées d'un canvas spécifique
    path('canvas/<int:pk>/statistics/', views.canvas_statistics, name='canvas-statistics'),
]
