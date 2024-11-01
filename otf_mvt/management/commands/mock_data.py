# your_app/management/commands/generate_mock_data.py

import os
from datetime import timedelta

from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth.models import User
from otf_mvt.models import Action, Person, Vote  # Remplacez `your_app` par le nom de votre application
from django.db import transaction

fake = Faker()


class Command(BaseCommand):
    help = 'Génère des données fictives pour les utilisateurs, les actions et les sous-actions.'

    def handle(self, *args, **kwargs):
        self.create_mock_data()

    def create_mock_data(self):
        persons = self.create_users()
        self.create_actions_and_subactions(persons)
        self.stdout.write(self.style.SUCCESS('Données fictives générées avec succès.'))

    def create_users(self):
        """Crée trois utilisateurs fictifs."""
        persons = []
        for i in range(3):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password=fake.password(length=12)
            )
            person = Person.objects.create(
                user=user,
                name=fake.name(),
            )
            persons.append(person)
        return persons

    @transaction.atomic
    def create_actions_and_subactions(self, persons):
        """Crée des actions et des sous-actions fictives avec des financements et des durées."""
        parent_actions = []
        for _ in range(5):  # Crée 5 actions principales
            action = Action.objects.create(
                name=fake.sentence(nb_words=6),
                description=fake.paragraph(nb_sentences=3),
                target=fake.random_number(digits=5),
                total_price_paid=fake.random_number(digits=4),
                currency='USD',
                duration=timedelta(days=fake.random_number(digits=3)),
            )
            for person in persons:
                action.add_participant(person)
                self.create_votes(action, person)
            parent_actions.append(action)

        for parent in parent_actions:
            for _ in range(2):  # Chaque action principale a 2 sous-actions
                sub_action = Action.objects.create(
                    name=fake.sentence(nb_words=6),
                    description=fake.paragraph(nb_sentences=3),
                    target=fake.random_number(digits=5),
                    total_price_paid=fake.random_number(digits=4),
                    currency='EUR',
                    duration=timedelta(days=fake.random_number(digits=3)),
                    parent_action=parent
                )
                for person in persons:
                    sub_action.add_participant(person)
                    self.create_votes(sub_action, person)

    def create_votes(self, action, person):
        """Crée des votes pour une action par un utilisateur."""
        vote_value = fake.random_element(elements=(-1, 1))  # Vote positif ou négatif
        Vote.objects.create(
            action=action,
            voter=person,
            vote_value=vote_value
        )