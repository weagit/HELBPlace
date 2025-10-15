from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from blog.models import Canvas  # Importation correcte du modèle Canvas pour récupérer les toiles
from django.contrib.auth.models import User
from django.http import Http404

# Fonction pour l'inscription des nouveaux utilisateurs
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)  # Instancier le formulaire d'inscription
        if form.is_valid():
            form.save()  # Sauvegarder le nouvel utilisateur
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in!')  # Message de succès
            return redirect('login')  # Rediriger vers la page de login
    else:
        form = UserRegisterForm()  # Si la méthode est GET, créer un formulaire vide
    return render(request, 'users/register.html', {'form': form})  # Rendu du template d'inscription


# Vue pour afficher le profil d'un utilisateur spécifique
@login_required
def user_profile(request, username):
    try:
        user = User.objects.get(username=username)  # Récupérer l'utilisateur par son nom d'utilisateur
    except User.DoesNotExist:
        raise Http404("User not found")  # Si l'utilisateur n'existe pas, lever une erreur 404

    # Récupérer les toiles dans lesquelles l'utilisateur a contribué
    canvases_contributed = Canvas.objects.filter(contributions__has_key=str(user.id))

    # Créer une liste contenant les toiles avec le nombre de contributions de l'utilisateur
    canvases_with_contributions = []
    for canvas in canvases_contributed:
        contributions_count = len(canvas.contributions.get(str(user.id), []))  # Compter le nombre de contributions
        canvases_with_contributions.append((canvas, contributions_count))  # Ajouter la toile et son nombre de contributions

    context = {
        'user': user,
        'canvases_with_contributions': canvases_with_contributions,  # Passer la liste des toiles et des contributions
    }

    return render(request, 'users/profile.html', context)  # Rendu du profil de l'utilisateur


# Vue pour gérer la mise à jour de son propre profil
@login_required
def profile(request):
    # Formulaire pour mettre à jour l'utilisateur et son profil
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)  # Formulaire pour les informations de l'utilisateur
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)  # Formulaire pour la mise à jour de l'image du profil
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()  # Sauvegarder les modifications des informations utilisateur
            p_form.save()  # Sauvegarder les modifications de l'image de profil
            messages.success(request, f'Your account has been updated!')  # Message de succès
            return redirect('profile')  # Rediriger vers la page de profil mise à jour
        
    else:
        u_form = UserUpdateForm(instance=request.user)  # Formulaire d'utilisateur pré-rempli
        p_form = ProfileUpdateForm(instance=request.user.profile)  # Formulaire de profil pré-rempli

    # Récupérer toutes les toiles dans lesquelles l'utilisateur a contribué
    canvases_contributed = Canvas.objects.filter(contributions__has_key=str(request.user.id))

    # Ajouter le nombre de contributions à chaque toile
    canvases_with_contributions = []
    for canvas in canvases_contributed:
        contributions_count = len(canvas.contributions.get(str(request.user.id), []))
        canvases_with_contributions.append((canvas, contributions_count))

    # Trier les toiles par nombre de contributions (de la plus grande à la plus petite)
    canvases_with_contributions.sort(key=lambda x: x[1], reverse=True)

    context = {
        'u_form': u_form,  # Passer le formulaire d'utilisateur
        'p_form': p_form,  # Passer le formulaire de profil
        'canvases_with_contributions': canvases_with_contributions  # Passer la liste triée des toiles et des contributions
    }

    return render(request, 'users/profile.html', context)  # Rendu du profil utilisateur avec les informations et les toiles
