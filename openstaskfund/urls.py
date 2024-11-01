from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('otf_mvt.urls')),  # Redirige vers les URLs de l'application `otf_mvt`
]

