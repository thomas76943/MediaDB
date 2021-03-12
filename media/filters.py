import django_filters
from .models import *

class filmFilter(django_filters.FilterSet):
    class Meta:
        model = Film
        fields = [
            'title',
            'release',
            'boxOffice',
            'rating',
        ]
