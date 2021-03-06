__author__ = 'Alok'

from time import time

from django.core.management.base import BaseCommand, CommandError
from feeds.models import Category, Log, Tweet


class Command(BaseCommand):
    help = 'Schedules task routines'

    # cron
    # */15 * * * * /root/.virtualenvs/twn-env/bin/python3 manage.py load_tweets

    def handle(self, *args, **kwargs):
        log = Log(task='load_tweets')
        try:
            t = -time()
            count = Category.refresh_all(50)
            t += time()
            log.success = True
            tweet_count = Tweet.objects.count()
            log.info = {'docs_updated': count, 'all': tweet_count, 'task_duration': int(t)}
        except Exception as e:
            log.success = False
            log.info = {'exception': str(e)}

        log.save()
        # self.stdout.write('task completed!')
