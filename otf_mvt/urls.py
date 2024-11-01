# urls.py dans l'application `otf_mvt`
from django.urls import path
from . import views

app_name = 'otf_mvt'

urlpatterns = [
    path('', views.index, name='index'),  # Page d'accueil qui affiche les fonctionnalités
]
