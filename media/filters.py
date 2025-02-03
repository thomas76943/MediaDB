import django_filters
from .models import *

from django_filters import DateFilter
from django_filters import ChoiceFilter



class filmFilter(django_filters.FilterSet):
    ratings = (('PG', 'PG'), ('PG-13', 'PG-13'), ('R', 'R'))
    rating = ChoiceFilter(field_name="rating", choices=ratings, empty_label='Any Age Rating')
    date = DateFilter(field_name="release", lookup_expr="gte", label="Release After")

    class Meta:
        model = Film
        fields = [
            'title','rating','release'
        ]

#class televisionFilter(django_filters.FilterSet):
#
#    date = DateFilter(field_name="release", lookup_expr="gte", label="Release After")
#    class Meta:
#        model = Television
#        fields = [
#            'release'
#        ]

class videoGameFilter(django_filters.FilterSet):

    date = DateFilter(field_name="release", lookup_expr="gte", label="Release After")
    class Meta:
        model = VideoGame
        fields = [
            'release'
        ]

class bookFilter(django_filters.FilterSet):

    date = DateFilter(field_name="release", lookup_expr="gte", label="Release After")
    class Meta:
        model = Book
        fields = [
            'release'
        ]

class webSeriesFilter(django_filters.FilterSet):

    date = DateFilter(field_name="release", lookup_expr="gte", label="Release After")
    class Meta:
        model = WebSeries
        fields = [
            'release'
        ]