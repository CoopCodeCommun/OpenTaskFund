# urls.py dans l'application `otf_mvt`
from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'action', views.ActionViewSet, basename='action')

urlpatterns = [
                  path('', views.index, name='index'),  # Page d'accueil qui affiche les fonctionnalités
              ] + router.urls
