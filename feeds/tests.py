import json
import os
import time

from django.test import TestCase
from django.conf import settings

from .models import Tweet, TwitterApi, Category, Channel

# channel info # https://api.twitter.com/1.1/users/show.json?screen_name=cnn&user_id=759251
# status # https://api.twitter.com/1.1/statuses/user_timeline.json?count=10&trim_user=true&exclude_replies=true&
# include_rts=false&screen_name=cnn

'''
// Javascript code to lazy load feeds
twttr.widgets.load(
  document.getElementById("container")
);
'''


class TweetsTestCase(TestCase):
    TWEETS_FILE = 'cnn_tweets_20.json'

    def setUp(self):
        path = os.path.join(settings.BASE_DIR, 'feeds/test_cases', self.TWEETS_FILE)


        # [tweet.save() for tweet in self.tweets]

    def test_to_json(self):
        """ placeholder comment """
        '''
        [print(tweet.to_json()) for tweet in self.tweets]
        c = Channel.objects.get(channel_id="759251")
        c.tweets = self.tweets
        c.save()
        '''


class TwitterApiTestCase(TestCase):
    def test_obtain_bearer_token(self):
        # first remove the already presend bearer_token
        api = TwitterApi.objects.first()
        self.assertEquals(True, api.obtain_bearer_token())

    def test_remove_token(self):
        # first create a random token
        api = TwitterApi(consumer_key='foo', consumer_secret="bar", bearer_token="disco")
        api.save()
        api.remove_token()
        self.assertEquals(None, api.bearer_token)
        api.delete()

    def test_get_token(self):
        #
        token = TwitterApi.get_token()
        self.assertIsInstance(token, str)
        self.assertGreater(len(token.strip()), 0)

    def test_channel_info(self):
        doc = TwitterApi.channel_info('PMOIndia')
        self.assertIsInstance(doc, dict)
        # print(doc)

    def test_tweets_info(self):
        doc = TwitterApi.tweets_by_channel('PMOIndia', 10)
        self.assertIsInstance(doc, list)
        # print(doc)


class CategoryTestCase(TestCase):
    pass
    '''
    # The following piece of code was used to initialize all the channels and categories
    def setUp(self):
        self.categories = {'Politics': ['CNNPolitics', 'PMOIndia', 'HuffPostPol', 'HuffPostIndia'], 'Tech': ['newsycombinator', 'techcrunch', 'gizmodo', 'recode', 'mashabletech'], 'Sports': ['StarSportsIndia', 'SportsCenter', 'ESPNcricinfo', 'HTSportsNews', 'BBCSport'], 'Entertainment': ['vine', 'cinema21', 'htshowbiz', 'PerezHilton', 'lifehacker'],  'Business': ['mashbusiness', 'EconomicTimes', 'forbes', 'TheEconomist', 'WSJ'], 'Health': ['_HEALTH_', 'WebMD', 'goodhealth', 'foodandwine',   'NYTHealth']}

    def test_insert(self):
        for category_text, channels in self.categories.items():
            category = Category(text=category_text)
            for screen_name in channels:
                raw_data = TwitterApi.channel_info(screen_name)
                channel = Channel.from_api(raw_data)
                category.channels.append(channel)
                print(category)
                time.sleep(1)

            category.save()
    '''
    def test_refresh(self):
        c = Category.objects(text='Tech').first()
        c.refresh(50)

