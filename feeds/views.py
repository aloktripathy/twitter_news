import datetime

from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer

from .models import Category, Tweet
from .serializers import CategorySerializer, TweetSerializer

'''
news.aloktripathy.com/api/tweets.json?category=Sports&sort_by=freshness&start_from=t&stop_at=t
news.aloktripathy.com/api/categories.json
'''


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def tweet_list(request):
    FEED_COUNT = 10

    tweets = Tweet.objects
    # add ranges
    if request.REQUEST.get('start_from'):
        t = datetime.datetime.fromtimestamp(int(request.REQUEST.get('start_from')))
        tweets = tweets.filter(created__gt=t)

    if request.REQUEST.get('until'):
        t = datetime.datetime.fromtimestamp(int(request.REQUEST.get('until')))
        tweets = tweets.filter(created__lte=t)

    page_number = int(request.REQUEST.get('page', 1))
    pagination_range = (page_number-1) * FEED_COUNT, page_number * FEED_COUNT
    print(pagination_range)

    tweets = tweets[pagination_range[0]:pagination_range[1]]

    # filter catagory
    if request.REQUEST.get('category'):
        tweets = tweets.filter(category=request.REQUEST.get('category'))

    # rank documents
    sort_by = request.REQUEST.get('sort_by', 'score')
    tweets = tweets.order_by('-score')




    serializer = TweetSerializer(tweets, many=True)
    return JSONResponse(serializer.data)


def category_list(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return JSONResponse(serializer.data)
