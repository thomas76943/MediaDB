import django_filters
from .models import *

from django_filters import DateFilter
from django_filters import ChoiceFilter



class filmFilter(django_filters.FilterSet):
    ratings = (('PG', 'PG'), ('PG-13', 'PG-13'), ('R', 'R'))
    rating = ChoiceFilter(field_name="rating", choices=ratings, empty_label='Rating')
    date = DateFilter(field_name="release", lookup_expr="gte", label="Release After")

    class Meta:
        model = Film
        fields = [
            'title',
        ]

