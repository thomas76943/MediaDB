from django import forms
from .models import *
from users.models import *

class DateInput(forms.DateInput):
    input_type = 'date'

#Base mapping contribution ModelForm used by base contribution CreateView class
#(Film Person Mapping Form)
class BaseMappingForm(forms.ModelForm):
    class Meta:
        model = FilmPersonMapping
        fields = ['film', 'person', 'role', 'character', 'billing']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].empty_label = None

#Film Genre Form
class FilmGenreMappingForm(BaseMappingForm):
    class Meta:
        model = FilmGenreMapping
        fields = ['film', 'genre']

#Film Company Form
class FilmCompanyMappingForm(BaseMappingForm):
    class Meta:
        model = FilmCompanyMapping
        fields = ['film', 'company', 'role']

#Film Tag Form
class FilmTagMappingForm(BaseMappingForm):
    class Meta:
        model = FilmTagMapping
        fields = ['film', 'tag']

#TV Person Form
class TelevisionPersonMappingForm(BaseMappingForm):
    class Meta:
        model = TelevisionPersonMapping
        fields = ['television', 'person', 'role', 'character', 'billing']

#TV Genre Form
class TelevisionGenreMappingForm(BaseMappingForm):
    class Meta:
        model = TelevisionGenreMapping
        fields = ['television', 'genre']

#TV Company Form
class TelevisionCompanyMappingForm(BaseMappingForm):
    class Meta:
        model = TelevisionCompanyMapping
        fields = ['television', 'company', 'role']

#TV Tag Form
class TelevisionTagMappingForm(BaseMappingForm):
    class Meta:
        model = TelevisionTagMapping
        fields = ['television', 'tag']

#Video Game Person Form
class VideoGamePersonMappingForm(BaseMappingForm):
    class Meta:
        model = VideoGamePersonMapping
        fields = ['videogame', 'person', 'role', 'character', 'billing']

#Video Game Genre Form
class VideoGameGenreMappingForm(BaseMappingForm):
    class Meta:
        model = VideoGameGenreMapping
        fields = ['videoGame', 'genre']

#Video Game Company Form
class VideoGameCompanyMappingForm(BaseMappingForm):
    class Meta:
        model = VideoGameCompanyMapping
        fields = ['videoGame', 'company', 'role']

#Video Game Tag Form
class VideoGameTagMappingForm(BaseMappingForm):
    class Meta:
        model = VideoGameTagMapping
        fields = ['videoGame', 'tag']

#Video Game Console Form
class VideoGameConsoleMappingForm(BaseMappingForm):
    class Meta:
        model = VideoGameConsoleMapping
        fields = ['videoGame', 'console']

#Book Person Form
class BookPersonMappingForm(BaseMappingForm):
    class Meta:
        model = BookPersonMapping
        fields = ['book', 'person', 'role']

#Book Genre Form
class BookGenreMappingForm(BaseMappingForm):
    class Meta:
        model = BookGenreMapping
        fields = ['book', 'genre']

#Book Company Form
class BookCompanyMappingForm(BaseMappingForm):
    class Meta:
        model = BookCompanyMapping
        fields = ['book', 'company', 'role']

#Book Tag Form
class BookTagMappingForm(BaseMappingForm):
    class Meta:
        model = BookTagMapping
        fields = ['book', 'tag']

#Web Series Person Form
class WebSeriesPersonMappingForm(BaseMappingForm):
    class Meta:
        model = WebSeriesPersonMapping
        fields = ['webSeries', 'person', 'role']

#Web Series Genre Form
class WebSeriesGenreMappingForm(BaseMappingForm):
    class Meta:
        model = WebSeriesGenreMapping
        fields = ['webSeries', 'genre']

#Web Series Company Form
class WebSeriesCompanyMappingForm(BaseMappingForm):
    class Meta:
        model = WebSeriesCompanyMapping
        fields = ['webSeries', 'company', 'role']

#Web Series Tag Form
class WebSeriesTagMappingForm(BaseMappingForm):
    class Meta:
        model = WebSeriesTagMapping
        fields = ['webSeries', 'tag']