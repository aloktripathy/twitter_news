__author__ = 'Alok'

from django.core.management.base import BaseCommand, CommandError
from feeds.models import Category, Log, Tweet


class Command(BaseCommand):
    help = 'Schedules task routines'

    # cron
    # */15 * * * * /root/.virtualenvs/twn-env/bin/python3 manage.py load_tweets

    def handle(self, *args, **kwargs):
        log = Log(task='load_tweets')
        try:
            count = Category.refresh_all(50)
            log.success = True
            tweet_count = Tweet.objects.count()
            log.info = {'docs_updated': count, 'all': tweet_count}
        except Exception as e:
            log.success = False
            log.info = {'exception': str(e)}

        self.stdout.write('Tweets loaded successfully')
