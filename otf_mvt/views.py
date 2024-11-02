# views.py
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from .models import Action, Vote


def index(request):
    """
    Vue pour afficher toutes les actions dans une liste de cartes.
    """
    rand_user = User.objects.order_by('?').first()
    login(request, rand_user)
    print(rand_user)
    actions = (Action.objects.filter(parent__isnull=True)
               .prefetch_related('children'))

    context = {'actions': actions}
    return render(request, 'index.html', context)


class ActionViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny,]
    authentication_classes = [SessionAuthentication, ]

    @action(detail=True, methods=['get'])
    def vote(self, request, pk=None):
        action = get_object_or_404(Action, pk=pk)
        user = request.user

        if user.is_authenticated:
            Vote.objects.get_or_create(action=action, voter=user.person, vote_value=1)
            action.refresh_from_db()

        # Return the button with the updated vote count
        html_content = f'<button class="btn btn-small btn-success">{action.total_votes}</button>'
        return HttpResponse(html_content, content_type="text/html")
