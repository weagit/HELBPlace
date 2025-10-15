from datetime import timezone
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.http import JsonResponse
from .models import Canvas
import requests
from django.db.models import Count


# Page d'accueil : liste tous les canvas
class CanvasListView(ListView):
    model = Canvas
    template_name = 'blog/home.html'  # Le template utilisé pour la page d'accueil
    context_object_name = 'canvases'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Convertir le contenu en JSON valide pour l'utiliser dans le template
        for canvas in context['canvases']:
            canvas.content = json.dumps(canvas.content)
        return context

    def get_queryset(self):
        # Trier uniquement par nombre de contributions
        return Canvas.objects.annotate(num_contributions=Count('contributions')).order_by('-num_contributions')  # Trier uniquement par nombre de contributions
    
# Détail d'un canvas
class CanvasDetailView(LoginRequiredMixin, DetailView):
    model = Canvas
    template_name = 'blog/canvas_detail.html'
    context_object_name = 'canvas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Encoder le contenu en JSON valide
        context['content_json'] = json.dumps(self.object.content)
        
         # Vérifier si l'utilisateur est le créateur et ajouter un bouton de suppression
        if self.object.author == self.request.user:
            context['can_delete'] = True
        else:
            context['can_delete'] = False
        return context

# Créer un nouveau canvas
class CanvasCreateView(LoginRequiredMixin, CreateView):
    model = Canvas
    fields = ['title', 'width', 'height', 'pixel_edit_interval']

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        # Initialise la toile après création
        self.object.initialize_canvas()
        return response




# Statistique d'un canvas
class CanvasStatisticsView(DetailView):
    model = Canvas
    template_name = 'blog/canvas_statistics.html'  # Template à créer pour afficher les statistiques
    context_object_name = 'canvas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupérer les statistiques de la toile
        statistics = self.object.get_statistics()

        # Ajouter les statistiques au contexte
        context['daily_contributions'] = statistics['daily_contributions']
        context['top_contributors'] = statistics['top_contributors']

        return context

# Supprimer un canvas
class CanvasDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Canvas
    success_url = '/'

    def test_func(self):
        canvas = self.get_object()
        if self.request.user == canvas.author:
            return True
        return False


# API pour mettre à jour les pixels
@csrf_exempt
@login_required
def update_pixel(request, pk):
    if request.method == 'POST':
        try:
            canvas = Canvas.objects.get(pk=pk)
            x, y, color = json.loads(request.body).get("x"), json.loads(request.body).get("y"), json.loads(request.body).get("color")
            
            # Essayer de mettre à jour le pixel
            success = canvas.update_pixel(x, y, color, request.user)

            if success:
                return JsonResponse({"message": "Pixel updated successfully!"}, status=200)
            else:
                # Si l'utilisateur essaie de modifier trop tôt
                time_left = canvas.pixel_edit_interval - (timezone.now().timestamp() - canvas.last_edit_timestamps.get(str(request.user.id), 0))
                return JsonResponse({"error": f"Please wait {int(time_left)} seconds before editing again."}, status=403)
                
        except Canvas.DoesNotExist:
            return JsonResponse({"error": "Canvas not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method"}, status=405)



# API pour récupérer les données d'un canvas
@login_required
def get_canvas_data(request, pk):
    """Récupère les données actuelles du canvas pour mise à jour dynamique."""
    try:
        canvas = Canvas.objects.get(pk=pk)
        return JsonResponse({'content': json.dumps(canvas.content)}, status=200)
    except Canvas.DoesNotExist:
        return JsonResponse({'error': 'Canvas not found'}, status=404)




def community(request):
    # Récupérer les données du fichier colors.txt
    url = "https://helbplace2425.alwaysdata.net/colors.txt"
    response = requests.get(url)

    # Si la requête réussit
    if response.status_code == 200:
        # Séparer chaque ligne du fichier en une liste
        pixel_data = response.text.strip().split('\n')
        
        # Construire un tableau 2D avec les couleurs des pixels
        canvas_data = [line.split(';') for line in pixel_data]

        # Calculer la largeur et la hauteur du canvas
        canvas_width = len(canvas_data[0])  # Nombre de pixels dans la première ligne
        canvas_height = len(canvas_data)    # Nombre de lignes dans le tableau

        # Multiplier les dimensions par 10 pour afficher les pixels correctement
        scaled_width = canvas_width * 10
        scaled_height = canvas_height * 10

        # Passer ces données au template
        context = {
            'canvas_data': canvas_data,
            'canvas_width': scaled_width,
            'canvas_height': scaled_height,
        }

        return render(request, 'blog/community.html', context)
    else:
        # En cas d'erreur avec la requête, afficher un message d'erreur
        return render(request, 'blog/community.html', {'error': 'Unable to fetch canvas data'})


# Méthode pour mettre à jour un pixel sur la toile de la community B2
def updatePixelCommunity(request):
    # Récupérer les données du formulaire
    username = "ewalid"  # Remplace par ton nom d'utilisateur
    password = "FOWoegXfasE9"  # Remplace par ton mot de passe
    row_index = request.GET.get('row')  # Index de la ligne
    col_index = request.GET.get('col')  # Index de la colonne
    hex_value = request.GET.get('hexvalue')  # Valeur hexadécimale du pixel

    # URL de la mise à jour du pixel
    url = f"https://helbplace2425.alwaysdata.net/writer.php?username={username}&password={password}&row={row_index}&col={col_index}&hexvalue={hex_value}"

    # Effectuer la requête GET pour mettre à jour le pixel
    response = requests.get(url)

    if response.status_code == 200:
        return JsonResponse({'status': 'success', 'message': 'Pixel updated successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Failed to update pixel'})
    

# Vue pour afficher les statistiques d'un canvas
@login_required
def canvas_statistics(request, pk):
    try:
        canvas = Canvas.objects.get(pk=pk)
        
        # Récupérer les statistiques de la toile
        statistics = canvas.get_statistics()  # Retourne un dictionnaire

        # Structure des données pour passer au template
        daily_contributions = statistics['daily_contributions']
        top_contributors = statistics['top_contributors']
        
        # Formatage des dates au format ISO pour être utilisables dans le template
        formatted_dates = [date.isoformat() for date in daily_contributions['dates']]

        # Passer les données de statistiques au template
        context = {
            'canvas': canvas,
            'daily_contributions': {
                'dates': formatted_dates,  # Les dates formatées
                'counts': daily_contributions['counts']
            },
            'top_contributors': top_contributors,        # Contient les contributeurs et leurs contributions
        }
        return render(request, 'blog/canvas_statistics.html', context)
    
    except Canvas.DoesNotExist:
        return JsonResponse({'error': 'Canvas not found'}, status=404)


