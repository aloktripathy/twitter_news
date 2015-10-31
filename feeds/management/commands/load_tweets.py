__author__ = 'Alok'

from django.core.management.base import BaseCommand, CommandError
from feeds.models import Category


class Command(BaseCommand):
    help = 'Schedules task routines'

    # cron
    # */15 * * * * /root/.virtualenvs/twn-env/bin/python3 manage.py load_tweets

    def handle(self, *args, **kwargs):
        Category.refresh_all(50)
        self.stdout.write('Tweets loaded successfully')