from django import forms
from .models import *
from users.models import *

class DateInput(forms.DateInput):
    input_type = 'date'

class ContributePersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = ['firstName', 'surname', 'DoB', 'alive', 'DoD', 'imageFilePath', 'bio']
        widgets = {
            'firstName':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'surname':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Surname'}),
            'DoB':DateInput(),
            'DoD': DateInput(),
            'bio':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bio'}),
            'imageFilePath': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image File Path'}),

        }

class ContributeFilmForm(forms.ModelForm):
    class Meta:
        model = Film
        fields = ['title', 'release', 'rating', 'synopsis', 'length', 'budget',
                  'boxOffice', 'posterFilePath', 'trailerVideoPath']

        widgets = {
            'title':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'release':DateInput(),
            'rating':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Rating'}),
            'synopsis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Synopsis'}),
            'length': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Length (mins)'}),
            'budget': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Budget'}),
            'boxOffice': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Box Offce'}),
            'posterFilePath': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Poster File Path'}),
            'trailerVideoPath': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trailer Video Path'}),
        }

class ContributeTelevisionForm(forms.ModelForm):
    class Meta:
        model = Television
        fields = ['title', 'ongoing', 'release', 'end', 'synopsis', 'seasons',
                  'episodes', 'posterFilePath', 'trailerVideoPath']

        widgets = {
            'title':forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title'}),
            'release':DateInput(),
            'end': DateInput(),
            'synopsis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Synopsis'}),
            'seasons': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Seasons'}),
            'episodes': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Episodes'}),
            'posterFilePath': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Poster File Path'}),
            'trailerVideoPath': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trailer Video Path'}),
        }

class filmRatingForm(forms.Form):
    class Meta:
        model = FilmRating
        fields = ['user', 'film', 'rating', 'review']

        widgets = {
            'rating':forms.FloatField()
        }