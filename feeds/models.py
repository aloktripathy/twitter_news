import math
import urllib.parse
import base64
import requests
import json
import time

from django.utils import timezone

from mongoengine import *


# {category: 1, score: -1}, {created: -1}, {category: 1, created: -1}
class Tweet(Document):
    """
    Represents a tweet document with 24 hours of lifetime
    """
    _id = IntField(primary_key=True)
    tweet_link = URLField()
    category = StringField()

    embedded_link = URLField(null=True)
    media = URLField(null=True)
    text = StringField()

    favo
    score = IntField()
    created = DateTimeField()

    meta = {
        'indexes': [
            {'fields': ['created'], 'expireAfterSeconds': 3600 * 24}
        ]
    }

    @staticmethod
    def from_api(data, category, channel_screen_name):
        # print(data)
        """
        Takes a raw tweet object retrieved from API and it's category to spit out as a Tweet document
        Important: Doesn't save the Tweet document to db
        """
        # tweet = Tweet(category=category)
        # tweet._id = int(data["id_str"])
        # tweet.tweet_link = data['extended_entities']['media'][0]['expanded_url']

        t = {"_id": int(data["id_str"]), "category": category, "text": data["text"],
             "tweet_link": "https://www.twitter.com/{0}/status/{1}".format(channel_screen_name, data["id_str"])
             }

        try:
            # tweet.embedded_link = data['entities']['urls'][0]['url']
            t['embedded_link'] = data['entities']['urls'][0]['url']
        except (KeyError, IndexError):
            pass
        try:
            # tweet.media = data['entities']['media'][0]['media_url']
            t['media'] = data['entities']['media'][0]['media_url']
        except (KeyError, IndexError):
            pass

        t['favorites'], t['retweets'], time_str = data["retweet_count"], data["favorite_count"], data["created_at"]
        timestamp = timezone.datetime.strptime(time_str, "%a %b %d %H:%M:%S %z %Y")



        # tweet.score = Tweet._compute_score(t['favorites'], t['retweets'], timestamp.timestamp())
        t['score'] = Tweet._compute_score(t['favorites'], t['retweets'], timestamp.timestamp())
        # tweet.created = timestamp
        t['created'] = timestamp
        return t
        # return tweet

    @staticmethod
    def _compute_score(favorites, retweets, timestamp):
        """
        An exponential time decay algorithm to measure the trendiness of a tweet based on it's retweets,
        favorites count and age
        """
        TIME_ZERO = 1446170525
        ROLLING_PERIOD = 3600

        time_gap = timestamp - TIME_ZERO
        points = max(1, favorites + retweets)   # avoid log(0) case
        order = math.log(points, 2)
        return round(order + time_gap / ROLLING_PERIOD)


class Channel(EmbeddedDocument):
    """
    Represents a twitter account being used as a news source
    """
    channel_id = IntField(unique=True)
    screen_name = StringField(unique=True)
    name = StringField()
    profile_pic = URLField()

    @staticmethod
    def from_api(data):
        return Channel(channel_id=data['id'], screen_name=data['screen_name'],
                       name=data['name'], profile_pic=data['profile_image_url_https'])


class Category(Document):
    """
    Represents a news feed category
    """
    text = StringField(unique=True)
    channels = EmbeddedDocumentListField(Channel)
    last_refreshed = DateTimeField(default=timezone.now())

    def refresh(self, feed_count_per_channel=50):
        """
        refresh all the channels under this category
        """
        for channel in self.channels:
            # fetch tweets under channel using API
            raw_tweets = TwitterApi.tweets_by_channel(channel.screen_name, feed_count_per_channel)
            for raw_tweet in raw_tweets:
                # upsert instead of inserting
                # Tweet.from_api(raw_tweet, self.text).save()
                data = Tweet.from_api(raw_tweet, self.text, channel.screen_name)

                # manipulation for upsert-modify
                kargs = {'set__'+k: v for k, v in data.items()}
                kargs['upsert'] = True
                kargs['new'] = True
                Tweet.objects(_id=data['_id']).modify(**kargs)

            time.sleep(1)
            self.last_refreshed = timezone.now()
            self.save()

    @staticmethod
    def refresh_all(feed_count_per_channel=50):
        """
        refreshes all the categories and the channels under them
        """
        categories = Category.objects.all()

        for category in categories:
            category.refresh(feed_count_per_channel)


class TwitterApiError(Exception):
    pass


class TwitterApi(Document):
    """
    This class exposes the app to Twitter data
    Keeps various settings/keys in the db
    """
    OAUTH2_TOKEN_URL = 'https://api.twitter.com/oauth2/token'
    CHANNEL_INFO_URL = 'https://api.twitter.com/1.1/users/show.json'
    TWEETS_URL = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    bearer_token_cached = None

    consumer_key = StringField()
    consumer_secret = StringField()
    bearer_token = StringField(null=True)

    def obtain_bearer_token(self):
        """
        Uses consumer_key and secret_key to authenticate and get a reusable access token
        Saves the access token to DB for future use
        :return: True if token successfully obtained
        """

        # url encode both the keys according to RFC 1738 and then join them using `:`
        credentials = ':'.join([urllib.parse.quote_plus(k) for k in (self.consumer_key, self.consumer_secret)])
        credentials_encoded = base64.b64encode(credentials.encode('ascii'))

        # make the POST request with appropriate body and header to obtain bearer token
        body = {'grant_type': 'client_credentials'}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Authorization': b'Basic ' + credentials_encoded
        }
        response = requests.post(TwitterApi.OAUTH2_TOKEN_URL, data=body, headers=headers)

        # print(response.headers, response.content)

        # application/json content-type spits out binary data, convert it to unicode and then json decode
        data = TwitterApi._bin_2_obj(response.content)

        # handle API errors
        if 'errors' in data:
            error = data['errors'][0]
            raise TwitterApiError('{0}: {1} [{2}]'.format(error.get('label'), error.get('message'), error.get('code')))

        # check whether both token_type and access_token exist in response body and if token_type is bearer
        if data.get('token_type') == 'bearer' and data.get('access_token'):
            # save bearer_token in db for future use
            self.bearer_token = data.get('access_token')
            self.save()

        # Something went wrong
        else:
            raise TwitterApiError('Unknown API error: something went wrong!')

        return True

    @staticmethod
    def get_token():
        """
        Fetches the bearer_token
        :return: <str> bearer_token
        """
        if TwitterApi.bearer_token_cached:
            return TwitterApi.bearer_token_cached

        api = TwitterApi.objects.first()

        # api found in db
        if not api:
            raise TwitterApiError('Twitter API keys were not found in database')

        if api.bearer_token:
            TwitterApi.bearer_token_cached = None
            return api.bearer_token
        elif api.obtain_bearer_token():
            return api.bearer_token

        return None

    def remove_token(self):
        """
        Removes the bearer_token from document
        :return: None
        """
        self.bearer_token = None
        self.save()

    @staticmethod
    def _api_request_header():
        return {'Authorization': 'Bearer ' + TwitterApi.get_token()}

    @staticmethod
    def _bin_2_obj(stream):
        return json.loads(stream.decode('utf-8'))

    @staticmethod
    def channel_info(screen_name=None):
        """
        Pulls publicly available info about the user/channel
        :return: None
        """
        params = {'screen_name': screen_name}
        return TwitterApi._fetch_from_remote(TwitterApi.CHANNEL_INFO_URL, params)

    @staticmethod
    def tweets_by_channel(screen_name, count, since_id=None):
        """
        Pulls publicly available tweets posted by channels
        :return: object
        """
        params = {'screen_name': screen_name, 'count': count,
                  'trim_user': True, 'exclude_replies': True,
                  'contributor_details': False, 'include_rts': False}

        if since_id:
            params['since_id'] = since_id
        return TwitterApi._fetch_from_remote(TwitterApi.TWEETS_URL, params)

    @staticmethod
    def _fetch_from_remote(url, params):
        response = requests.get(url, params, headers=TwitterApi._api_request_header())

        data = TwitterApi._bin_2_obj(response.content)

        if 'errors' in data:
            error = data['errors'][0]
            raise TwitterApiError('{0}: {1} [{2}]'.format(error.get('label'), error.get('message'), error.get('code')))

        return data
