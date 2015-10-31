__author__ = 'Alok'

from rest_framework_mongoengine.serializers import DocumentSerializer, EmbeddedDocumentSerializer
from rest_framework.serializers import ModelSerializer
from .models import Category, Tweet, Channel


class CustomModelSerializer(ModelSerializer):

    def _include_additional_options(self, *args, **kwargs):
        return self.get_extra_kwargs()

    def _get_default_field_names(self, *args, **kwargs):
        return self.get_field_names(*args, **kwargs)


class TweetSerializer(CustomModelSerializer, DocumentSerializer):
    class Meta:
        model = Tweet
        fields = ('tweet_link', 'category', 'favorites', 'retweets', 'score', 'created')


class CategorySerializer(CustomModelSerializer, DocumentSerializer):
    class Meta:
        model = Category
        fields = ('text', 'channels')
