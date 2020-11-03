from rest_framework import serializers
from .models import *


class FilmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = ('id', 'url', 'title', 'release', 'rating', 'synopsis', 'length', 'budget', 'boxOffice', 'poster')


class TelevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Television
        fields = ('id', 'url', 'title', 'release', 'synopsis', 'seasons', 'episodes', 'poster')

