from django.shortcuts import render

# Create your views here.


# views.py
from django.shortcuts import render
from .models import Feature

def index(request):
    """
    Vue pour afficher toutes les fonctionnalités dans une liste de cartes.
    """
    features = Feature.objects.all()  # Récupère toutes les fonctionnalités
    return render(request, 'index.html', {'features': features})
