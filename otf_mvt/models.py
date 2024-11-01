from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Person(models.Model):
    """
    Modèle pour représenter une personne qui pourrait être un créateur de fonctionnalité (feature), un sponsor ou un participant.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

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


class Feature(models.Model):
    """
    Modèle pour une fonctionnalité, composée de plusieurs tâches ayant chacune un coût.
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    creator = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, related_name="created_features")
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    tags = models.ManyToManyField(Tag, related_name="features", blank=True)
    currency = models.CharField(max_length=3, default="EUR")  # Devise pour le financement

    class Status(models.TextChoices):
        TO_DO = 'to_do', _('To Do')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TO_DO,
    )

    def __str__(self):
        return self.name

    @property
    def total_cost(self):
        """Calcul du coût total requis pour financer toutes les tâches."""
        return self.tasks.aggregate(total=models.Sum('cost'))['total'] or 0

    @property
    def total_funded(self):
        """Calcul du montant total financé pour toutes les tâches."""
        return self.tasks.aggregate(total=models.Sum('funded_amount'))['total'] or 0

    @property
    def funding_progress(self):
        """Calcul du pourcentage de financement total de la fonctionnalité."""
        if self.total_cost > 0:
            return min((self.total_funded / self.total_cost) * 100, 100)
        return 0


class Task(models.Model):
    """
    Modèle pour une tâche faisant partie d'une fonctionnalité, avec un coût individuel et un financement.
    """
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="tasks")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)  # Coût requis pour cette tâche
    funded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Montant financé pour cette tâche

    def __str__(self):
        return f"{self.name} ({self.cost} {self.feature.currency})"

    @property
    def funding_progress(self):
        """Retourne le pourcentage de financement de la tâche."""
        if self.cost > 0:
            return min((self.funded_amount / self.cost) * 100, 100)
        return 0

    def add_funding(self, amount):
        """
        Méthode pour ajouter du financement à la tâche.
        """
        self.funded_amount = min(self.funded_amount + amount, self.cost)  # Limite le financement au coût de la tâche
        self.save()


class Vote(models.Model):
    """
    Modèle pour enregistrer les votes sur les fonctionnalités (inspiré de schema.org: VoteAction).
    """
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="votes")
    voter = models.ForeignKey(Person, on_delete=models.CASCADE, related_name="votes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('feature', 'voter')  # Un vote par fonctionnalité et par personne

    def __str__(self):
        return f"Vote by {self.voter.name} on {self.feature.name}"


class Funding(models.Model):
    """
    Modèle pour gérer les contributions financières aux fonctionnalités (inspiré de schema.org: MonetaryAmount).
    """
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="funding")
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
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.name} on {self.feature.name}"
