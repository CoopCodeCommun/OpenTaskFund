from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _


class Person(models.Model):
    """
    Modèle pour représenter une personne qui pourrait être un créateur de fonctionnalité (feature), un sponsor ou un participant.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Modèle pour étiqueter les fonctionnalités avec des mots-clés (inspiré de schema.org: Keyword).
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Action(models.Model):
    """
    Modèle aligné avec Schema.org, pour gérer des actions et sous-actions avec
    financement, participants, et relations parent/enfant.
    """
    name = models.CharField(
        max_length=255,
        help_text=_("Le nom de l'action.")
    )
    description = models.TextField(
        blank=True,
        help_text=_("La description détaillée de l'action.")
    )
    target = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("L'objectif financier à atteindre pour cette action.")
    )
    total_price_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Le montant total financé pour cette action jusqu'à présent.")
    )
    currency = models.CharField(
        max_length=3,
        default="EUR",
        help_text=_("La monnaie utilisée pour les transactions financières de cette action.")
    )
    duration = models.DurationField(
        default=0,
        help_text=_("La durée totale travaillée sur cette action.")
    )
    parent_action = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="sub_actions",
        help_text=_("L'action parente de laquelle cette action fait partie, si applicable.")
    )
    participants = models.ManyToManyField(
        'Person',
        related_name="participating_actions",
        blank=True,
        help_text=_("Les utilisateurs participant à cette action.")
    )

    def __str__(self):
        return self.name

    @property
    def is_parent(self):
        """Détermine si cette action est une action principale (sans parent)."""
        return self.parent_action is None

    @property
    def total_price(self):
        """Calcule le coût total en incluant tous les enfants (sous-actions)."""
        return (
                self.sub_actions.aggregate(total=Sum('target'))['total'] or 0
        ) + self.target

    @property
    def funding_progress(self):
        """Calcule le pourcentage de financement atteint pour cette action."""
        if self.target > 0:
            return (self.total_price_paid / self.target) * 100
        return 0

    @property
    def aggregate_funded(self):
        """Calcule le financement total en incluant tous les enfants (sous-actions)."""
        return (
                self.sub_actions.aggregate(total=Sum('total_price_paid'))['total'] or 0
        ) + self.total_price_paid

    @property
    def aggregate_funding_progress(self):
        """Calcule le pourcentage de financement total en incluant tous les enfants."""
        if self.total_price > 0:
            return (self.aggregate_funded / self.total_price) * 100
        return 0

    @property
    def total_duration(self):
        """Calcule la durée totale travaillée, en incluant les sous-actions."""
        sub_actions_duration = self.sub_actions.aggregate(total=Sum('duration'))['total'] or 0
        return sub_actions_duration + self.duration

    def add_participant(self, user):
        """Ajoute un utilisateur comme participant à cette action."""
        self.participants.add(user)

    def remove_participant(self, user):
        """Retire un utilisateur des participants de cette action."""
        self.participants.remove(user)

    @property
    def participant_count(self):
        """Retourne le nombre total de participants pour cette action."""
        return self.participants.count()


class Vote(models.Model):
    """
    Modèle de vote basé sur Schema.org, permettant aux utilisateurs de voter pour une action.
    """
    action = models.ForeignKey(Action, on_delete=models.CASCADE,
                               related_name="votes")  # Cible du vote, nommée `action` pour correspondre au modèle Action
    voter = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="user_votes")  # Auteur du vote
    vote_value = models.IntegerField(
        default=1)  # Valeur du vote, pouvant être ajustée si un système de points est souhaité
    vote_date = models.DateTimeField(auto_now_add=True)  # Date du vote, enregistrée automatiquement

    class Meta:
        unique_together = ('action', 'voter')  # Empêche un utilisateur de voter plusieurs fois pour la même action

    def __str__(self):
        return f"Vote by {self.voter.name} on {self.action.name} (Value: {self.vote_value})"


class Funding(models.Model):
    """
    Modèle pour gérer les contributions financières aux fonctionnalités (inspiré de schema.org: MonetaryAmount).
    """
    action = models.ForeignKey(Action, on_delete=models.CASCADE, related_name="funding")
    contributor = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="contributions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")  # ISO currency code
    date_contributed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} {self.currency} by {self.contributor.name} for {self.feature.name}"


class Comment(models.Model):
    """
    Modèle pour les commentaires sur les fonctionnalités.
    """
    action = models.ForeignKey(Action, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.name} on {self.feature.name}"
