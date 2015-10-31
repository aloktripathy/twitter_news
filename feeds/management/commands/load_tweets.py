__author__ = 'Alok'

from django.core.management.base import BaseCommand, CommandError
from feeds.models import Category


class Command(BaseCommand):
    help = 'Schedules task routines'

    def handle(self, *args, **kwargs):
        Category.refresh_all(50)
        self.stdout.write('Tweets loaded successfully')