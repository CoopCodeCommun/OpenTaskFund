from django.shortcuts import render

# Create your views here.


# views.py
from django.shortcuts import render
from .models import Action


def index(request):
    """
    Vue pour afficher toutes les actions dans une liste de cartes.
    """
    actions = Action.objects.all()  # Récupère toutes les fonctionnalités
    context = {'actions': actions}
    return render(request, 'index.html', context)
