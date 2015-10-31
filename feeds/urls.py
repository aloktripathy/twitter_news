__author__ = 'Alok'

from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import category_list, tweet_list

urlpatterns = [
    url(r'^categories$', category_list),
    url(r'^tweets$', tweet_list),
]

urlpatterns = format_suffix_patterns(urlpatterns)
