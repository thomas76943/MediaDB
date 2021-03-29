from django import forms
from .models import *
from users.models import *

class DateInput(forms.DateInput):
    input_type = 'date'


class BaseMappingForm(forms.ModelForm):
    class Meta:
        model = FilmPersonMapping
        fields = ['film', 'person', 'role', 'character', 'billing']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].empty_label = None

class FilmGenreMappingForm(BaseMappingForm):
    class Meta:
        model = FilmGenreMapping
        fields = ['film', 'genre']

class FilmCompanyMappingForm(BaseMappingForm):
    class Meta:
        model = FilmCompanyMapping
        fields = ['film', 'company', 'role']

class FilmTagMappingForm(BaseMappingForm):
    class Meta:
        model = FilmTagMapping
        fields = ['film', 'tag']

class TelevisionPersonMappingForm(BaseMappingForm):
    class Meta:
        model = TelevisionPersonMapping
        fields = ['television', 'person', 'role', 'character', 'billing']

class TelevisionGenreMappingForm(BaseMappingForm):
    class Meta:
        model = TelevisionGenreMapping
        fields = ['television', 'genre']

class TelevisionCompanyMappingForm(BaseMappingForm):
    class Meta:
        model = TelevisionCompanyMapping
        fields = ['television', 'company', 'role']

class TelevisionTagMappingForm(BaseMappingForm):
    class Meta:
        model = TelevisionTagMapping
        fields = ['television', 'tag']

class VideoGamePersonMappingForm(BaseMappingForm):
    class Meta:
        model = VideoGamePersonMapping
        fields = ['videogame', 'person', 'role', 'character', 'billing']

class VideoGameGenreMappingForm(BaseMappingForm):
    class Meta:
        model = VideoGameGenreMapping
        fields = ['videoGame', 'genre']

class VideoGameCompanyMappingForm(BaseMappingForm):
    class Meta:
        model = VideoGameCompanyMapping
        fields = ['videoGame', 'company', 'role']

class VideoGameTagMappingForm(BaseMappingForm):
    class Meta:
        model = VideoGameTagMapping
        fields = ['videoGame', 'tag']

class VideoGameConsoleMappingForm(BaseMappingForm):
    class Meta:
        model = VideoGameConsoleMapping
        fields = ['videoGame', 'console']

class BookPersonMappingForm(BaseMappingForm):
    class Meta:
        model = BookPersonMapping
        fields = ['book', 'person', 'role']

class BookGenreMappingForm(BaseMappingForm):
    class Meta:
        model = BookGenreMapping
        fields = ['book', 'genre']

class BookCompanyMappingForm(BaseMappingForm):
    class Meta:
        model = BookCompanyMapping
        fields = ['book', 'company', 'role']

class BookTagMappingForm(BaseMappingForm):
    class Meta:
        model = BookTagMapping
        fields = ['book', 'tag']

class WebSeriesPersonMappingForm(BaseMappingForm):
    class Meta:
        model = WebSeriesPersonMapping
        fields = ['webSeries', 'person', 'role']

class WebSeriesGenreMappingForm(BaseMappingForm):
    class Meta:
        model = WebSeriesGenreMapping
        fields = ['webSeries', 'genre']

class WebSeriesCompanyMappingForm(BaseMappingForm):
    class Meta:
        model = WebSeriesCompanyMapping
        fields = ['webSeries', 'company', 'role']

class WebSeriesTagMappingForm(BaseMappingForm):
    class Meta:
        model = WebSeriesTagMapping
        fields = ['webSeries', 'tag']
