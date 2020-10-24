import profile
from itertools import chain
from operator import attrgetter

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.views import generic

from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from users.models import *

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created')
            return redirect('media-home')
    else:
        form = UserRegisterForm()

    context = {
        'form' : UserRegisterForm()
    }

    return render(request, 'users/register.html', context)

@login_required
def userProfile(request):
    if request.POST:
        userUpdateForm = UserUpdateForm(request.POST, instance=request.user)
        profileUpdateForm = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if userUpdateForm.is_valid() and profileUpdateForm.is_valid():
            userUpdateForm.save()
            profileUpdateForm.save()
            messages.success(request, f'Account Updated')
            return redirect('userProfile')

    else:
        userUpdateForm = UserUpdateForm(instance=request.user)
        profileUpdateForm = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'userUpdateForm' : userUpdateForm,
        'profileUpdateForm' : profileUpdateForm,
    }
    return render(request, 'users/userProfile.html', context)

class memberProfile(generic.DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = 'users/memberProfileDetail.html'
    context_object_name = "memberProfile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filmRatings = FilmRating.objects.filter(user=self.object.id)
        televisionRatings = TelevisionRating.objects.filter(user=self.object.id)
        videoGameRatings = VideoGameRating.objects.filter(user=self.object.id)
        bookRatings = BookRating.objects.filter(user=self.object.id)
        webSeriesRatings = WebSeriesRating.objects.filter(user=self.object.id)
        ratings = sorted(list(chain(filmRatings, televisionRatings, videoGameRatings, bookRatings, webSeriesRatings)), key=attrgetter('dateTime'), reverse=True)
        context['ratings'] = ratings[:8]

        profileSections = ProfileSection.objects.filter(profile__user=self.object.id)
        context['profileSections'] = profileSections

        if profileSections != None:
            for x in range(profileSections.count()):
                profileSectionFilms = ProfileSectionFilmMapping.objects.filter(profileSection__profile__user=self.object.id).filter(profileSection__sectionName=profileSections[x].sectionName)
                profileSectionTelevision = ProfileSectionTelevisionMapping.objects.filter(profileSection__profile__user=self.object.id).filter(profileSection__sectionName=profileSections[x].sectionName)
                profileSectionVideoGames = ProfileSectionVideoGameMapping.objects.filter(profileSection__profile__user=self.object.id).filter(profileSection__sectionName=profileSections[x].sectionName)
                profileSectionBooks = ProfileSectionBookMapping.objects.filter(profileSection__profile__user=self.object.id).filter(profileSection__sectionName=profileSections[x].sectionName)
                profileSectionWebSeries = ProfileSectionWebSeriesMapping.objects.filter(profileSection__profile__user=self.object.id).filter(profileSection__sectionName=profileSections[x].sectionName)

                completeProfileSection = sorted(list(chain(profileSectionFilms,
                                                           profileSectionTelevision,
                                                           profileSectionVideoGames,
                                                           profileSectionBooks,
                                                           profileSectionWebSeries)), key=attrgetter('orderInSection'))

                context[profileSections[x].sectionName] = completeProfileSection

        return context

class memberProfileActivity(memberProfile):
    template_name = 'users/memberProfileActivityDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filmRatings = FilmRating.objects.filter(user=self.object.id)
        televisionRatings = TelevisionRating.objects.filter(user=self.object.id)
        videoGameRatings = VideoGameRating.objects.filter(user=self.object.id)
        bookRatings = BookRating.objects.filter(user=self.object.id)
        webSeriesRatings = WebSeriesRating.objects.filter(user=self.object.id)
        ratings = sorted(list(chain(filmRatings, televisionRatings, videoGameRatings, bookRatings, webSeriesRatings)), key=attrgetter('dateTime'), reverse=True)
        context['ratings'] = ratings
        return context

