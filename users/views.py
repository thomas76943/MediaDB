import profile
from itertools import chain
from operator import attrgetter
import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.views import generic
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ProfileSectionForm
from media.models import *
from users.models import *

from media import views
from media.views import genreBasedRecommender, personBasedRecommender, getFeed, getAllActivity

from django import http
from django.http import QueryDict
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect

import pandas as pd
import numpy as np
from django_pandas.io import read_frame

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

class userList(generic.DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = 'users/userList.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['films'] = UserListFilmMapping.objects.filter(user=self.object.id)
        context['television'] = UserListTelevisionMapping.objects.filter(user=self.object.id)
        context['videoGames'] = UserListVideoGameMapping.objects.filter(user=self.object.id)
        context['books'] = UserListBookMapping.objects.filter(user=self.object.id)
        context['webSeries'] = UserListWebSeriesMapping.objects.filter(user=self.object.id)

        userFRatings = FilmRating.objects.filter(user=self.object.id)
        seen = []
        for ur in userFRatings:
            seen.append(ur.film)
        context['ratedFilms'] = seen

        userTRatings = TelevisionRating.objects.filter(user=self.object.id)
        seen = []
        for ur in userTRatings:
            seen.append(ur.television)
        context['ratedTV'] = seen

        userVGRatings = VideoGameRating.objects.filter(user=self.object.id)
        seen = []
        for ur in userVGRatings:
            seen.append(ur.videoGame)
        context['ratedVideoGames'] = seen

        userBRatings = BookRating.objects.filter(user=self.object.id)
        seen = []
        for ur in userBRatings:
            seen.append(ur.book)
        context['ratedBooks'] = seen

        userWSRatings = WebSeriesRating.objects.filter(user=self.object.id)
        seen = []
        for ur in userWSRatings:
            seen.append(ur.webSeries)
        context['ratedWebSeries'] = seen

        return context

class memberProfile(generic.UpdateView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = 'users/memberProfileDetail.html'
    context_object_name = "memberProfile"
    fields=[]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filmRatings = FilmRating.objects.filter(user=self.object.id)
        context['filmCount'] = filmRatings.count()
        televisionRatings = TelevisionRating.objects.filter(user=self.object.id)
        context['tvCount'] = televisionRatings.count()
        videoGameRatings = VideoGameRating.objects.filter(user=self.object.id)
        context['vgCount'] = videoGameRatings.count()
        bookRatings = BookRating.objects.filter(user=self.object.id)
        context['bookCount'] = bookRatings.count()
        webSeriesRatings = WebSeriesRating.objects.filter(user=self.object.id)
        context['wsCount'] = webSeriesRatings.count()
        ratings = sorted(list(chain(filmRatings, televisionRatings, videoGameRatings, bookRatings, webSeriesRatings)), key=attrgetter('dateTime'), reverse=True)
        context['ratings'] = ratings[:12]

        profileSections = ProfileSection.objects.filter(profile__user=self.object.id).order_by('order')
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

        context['newSectionForm'] = ProfileSectionForm

        if self.request.user.is_authenticated:
            allFollowing = UserFollows.objects.filter(userA=self.request.user)
            isFollowing = False
            for following in allFollowing:
                if following.userB == self.object:
                    isFollowing = True
                    break
            context['inList'] = isFollowing

        return context

    def post(self, request, *args, **kwargs):
        object = self.get_object()

        #Following the user
        if request.POST.get('toggle') == "add":
            f = UserFollows(userA=request.user, userB=object)
            f.save()

        #Unfollowing the user
        elif request.POST.get('toggle') == "remove":
            print("Unfollowing User")
            f = UserFollows.objects.filter(userA=request.user, userB=object)
            f.delete()

        #Reordering the Profile Sections
        elif request.POST.get('changing') == 'confirm':
            print("Changing Profile Sections")
            entries = QueryDict(request.POST.get('content'))
            print(entries)
            for index, entry_id in enumerate(entries.getlist('section[]')):
                entry = ProfileSection.objects.get(id=entry_id)
                entry.order = index
                entry.save()
            return http.HttpResponseRedirect('/user/' + object.username)

        #Creating new profile section
        else:
            newSectionName = request.POST.get('name')
            newSectionType = request.POST.get('type')
            s = ProfileSection(profile=object.profile, sectionName=newSectionName, type=newSectionType)
            s.save()

        return http.HttpResponseRedirect('/user/' + object.username)


class memberProfileActivity(memberProfile):
    template_name = 'users/memberProfileActivityDetail.html'



#----------------------------------------------------------------------------------------------------------------------------------------#
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def userRatingStats(mediaType, user):
    if mediaType == 'Films':
        df = read_frame(FilmRating.objects.filter(user=user), fieldnames=['film', 'rating'])
    if mediaType == 'Television':
        df = read_frame(TelevisionRating.objects.filter(user=user), fieldnames=['television', 'rating'])
    if mediaType == 'Video Games':
        df = read_frame(VideoGameRating.objects.filter(user=user), fieldnames=['videoGame', 'rating'])
    if mediaType == 'Books':
        df = read_frame(BookRating.objects.filter(user=user), fieldnames=['book', 'rating'])
    if mediaType == 'Web Series':
        df = read_frame(WebSeriesRating.objects.filter(user=user), fieldnames=['webSeries', 'rating'])

    #pd.set_option('display.float_format', lambda x: '%.0f' % x)

    fig, ax = plt.subplots(1, 1, figsize=(3,1.5))
    ax.hist(df['rating'], rwidth=0.9)

    ax.set_facecolor('#323238')

    rects = ax.patches
    labels = ['.5', '1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5']
    #for i in rects:
    #    labels.append(int(i.get_height()))

    largest = 0
    for rect, label in zip(rects, labels):
        height = rect.get_height()
        if height > largest:
            largest = height
        #ax.text(rect.get_x() + rect.get_width() / 2, height-0.1, label, ha='center', va='top', color='white')
        #ax.text(rect.get_x() + rect.get_width() / 2, height+0.01, label, ha='center', va='top', color='white')
        rect.set_facecolor('#0CA06B')

    for rect, label in zip(rects, labels):
        if rect.get_height() < largest*0.1:
            rect.set_height(largest*0.1)

    buffer = BytesIO()
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig(buffer, format='png', bbox_inches = 'tight', pad_inches = -0.1)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    return { 'mediaType':mediaType,
             'Number of Ratings':df['rating'].count(),
             'Mean':str(df['rating'].mean())[:4],
             'Mode Rating':str(df['rating'].mode())[3:-17],
             'Rating Standard Deviation':str(df['rating'].std())[:4],
             'hist':graphic }

class memberProfileStats(memberProfileActivity):
    template_name = 'users/memberProfileStatsDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['stats'] = [userRatingStats('Films', self.object.id),
                            userRatingStats('Television', self.object.id),
                            userRatingStats('Video Games', self.object.id),
                            userRatingStats('Books', self.object.id),
                            userRatingStats('Web Series', self.object.id)]

        #context['graphic'] = userRatingStats('Films', self.object.id)

        """
        genreRecommendations, genreScores = genreBasedRecommender(self.object.id)
        context['genreScores'] = {i: genreScores[i] for i in list(genreScores)[:20]}

        actorRecommendations, personScores = personBasedRecommender(self.object.id, 1)
        context['actorScores'] = {i: personScores[i] for i in list(personScores)[:20]}

        directorRecommendations, directorScores = personBasedRecommender(self.object.id, 2)
        context['directorScores'] = {i: directorScores[i] for i in list(directorScores)[:20]}

        writerRecommendations, writerScores = personBasedRecommender(self.object.id, 3)
        context['writerScores'] = {i: writerScores[i] for i in list(writerScores)[:20]}
        """

        return context



class profileSection(generic.UpdateView):
    model = ProfileSection
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = 'users/profileSectionEdit.html'
    context_object_name = "profileSection"
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entries = []
        if self.object.type == 'Films':
            entries = ProfileSectionFilmMapping.objects.filter(profileSection=self.object.id)
            context['media'] = json.dumps(list(Film.objects.values('title', 'slug')[:500]))
        elif self.object.type == 'Television':
            entries =  ProfileSectionTelevisionMapping.objects.filter(profileSection=self.object.id)
            context['media'] = json.dumps(list(Television.objects.values('title', 'slug')[:500]))
        elif self.object.type == 'Video Games':
            entries = ProfileSectionVideoGameMapping.objects.filter(profileSection=self.object.id)
            context['media'] = json.dumps(list(VideoGame.objects.values('title', 'slug')[:500]))
        elif self.object.type == 'Books':
            entries = ProfileSectionBookMapping.objects.filter(profileSection=self.object.id)
            context['media'] = json.dumps(list(Book.objects.values('title', 'slug')[:500]))
        elif self.object.type == 'Web Series':
            entries = ProfileSectionWebSeriesMapping.objects.filter(profileSection=self.object.id)
            context['media'] = json.dumps(list(WebSeries.objects.values('title', 'slug')[:500]))
        context['entries'] = sorted(list(entries), key=attrgetter('orderInSection'))
        return context

    def post(self, request, *args, **kwargs):

        object = self.get_object()
        username = object.profile.user.username

        if request.POST.get('newName') != None:
            newName = request.POST.get('newName')
            object.sectionName = newName
            object.save()
            return http.HttpResponseRedirect('/profile-section/' + object.slug)

        elif request.POST.get('addMedia') != None:
            print("adding media attempt")
            get = request.POST.get('addMedia')
            spl = get.split('/')
            mediaSlug = spl[len(spl)-1]

            if object.type == "Films":
                getFilm = Film.objects.filter(slug=mediaSlug)[0]
                sectionLength = 0
                for psfm in ProfileSectionFilmMapping.objects.filter(profileSection=object):
                    sectionLength += 1
                newMap = ProfileSectionFilmMapping(film=getFilm, profileSection=object, orderInSection=sectionLength+1)
                newMap.save()

            elif object.type == "Television":
                getTV = Television.objects.filter(slug=mediaSlug)[0]
                sectionLength = 0
                for pstm in ProfileSectionFilmMapping.objects.filter(profileSection=object):
                    sectionLength += 1
                newMap = ProfileSectionTelevisionMapping(television=getTV, profileSection=object, orderInSection=sectionLength + 1)
                newMap.save()

            elif object.type == "Video Games":
                getVG = VideoGame.objects.filter(slug=mediaSlug)[0]
                sectionLength = 0
                for psvgm in ProfileSectionVideoGameMapping.objects.filter(profileSection=object):
                    sectionLength += 1
                newMap = ProfileSectionVideoGameMapping(videoGame=getVG, profileSection=object, orderInSection=sectionLength + 1)
                newMap.save()

            elif object.type == "Books":
                getB = Book.objects.filter(slug=mediaSlug)[0]
                sectionLength = 0
                for psbm in ProfileSectionBookMapping.objects.filter(profileSection=object):
                    sectionLength += 1
                newMap = ProfileSectionBookMapping(book=getB, profileSection=object, orderInSection=sectionLength + 1)
                newMap.save()

            elif object.type == "Web Series":
                getWS = WebSeries.objects.filter(slug=mediaSlug)[0]
                sectionLength = 0
                for pswsm in ProfileSectionWebSeriesMapping.objects.all():
                    if pswsm.profileSection == object:
                        sectionLength += 1
                newMap = ProfileSectionWebSeriesMapping(webSeries=getWS, profileSection=object, orderInSection=sectionLength + 1)
                newMap.save()
            return http.HttpResponseRedirect('/profile-section/' + object.slug)

        elif request.POST.get('removeMedia') != None:
            print("removing media attempt")
            get = request.POST.get('removeMedia')
            if get[0] == 'f':
                getFilm = Film.objects.filter(slug=get[2:])[0]
                getMap = ProfileSectionFilmMapping.objects.filter(profileSection=object, film=getFilm)[0]
                getMap.delete()
            if get[0] == 't':
                getTV = Television.objects.filter(slug=get[2:])[0]
                getMap = ProfileSectionTelevisionMapping.objects.filter(profileSection=object, television=getTV)[0]
                getMap.delete()
            if get[0] == 'v':
                getVG = VideoGame.objects.filter(slug=get[2:])[0]
                getMap = ProfileSectionVideoGameMapping.objects.filter(profileSection=object, videoGame=getVG)[0]
                getMap.delete()
            if get[0] == 'b':
                getB = Book.objects.filter(slug=get[2:])[0]
                getMap = ProfileSectionBookMapping.objects.filter(profileSection=object, book=getB)[0]
                getMap.delete()
            if get[0] == 'w':
                getWS = WebSeries.objects.filter(slug=get[2:])[0]
                getMap = ProfileSectionWebSeriesMapping.objects.filter(profileSection=object, webSeries=getWS)[0]
                getMap.delete()
            return http.HttpResponseRedirect('/profile-section/' + object.slug)

        elif request.POST.get('changing') == 'confirm':
            print("change found")
            entries = QueryDict(request.POST.get('content'))
            print(entries)
            for index, entry_id in enumerate(entries.getlist('entry[]')):
                if object.type == 'Films':
                    entry = ProfileSectionFilmMapping.objects.get(id=entry_id)
                elif object.type == 'Television':
                    entry = ProfileSectionTelevisionMapping.objects.get(id=entry_id)
                elif object.type == 'Video Games':
                    entry = ProfileSectionVideoGameMapping.objects.get(id=entry_id)
                elif object.type == 'Books':
                    entry = ProfileSectionBookMapping.objects.get(id=entry_id)
                elif object.type == 'Web Series':
                    entry = ProfileSectionWebSeriesMapping.objects.get(id=entry_id)
                entry.orderInSection = index
                entry.save()
            return http.HttpResponseRedirect('/profile-section/' + object.slug)

        elif request.POST.get('delete') == 'confirm':
            print("delete found")
            thisSection = ProfileSection.objects.filter(id=object.id)
            thisSection.delete()
            url = "/user/"+username
            return redirect(url)


def activityFeed(request):
    context = {}
    if request.user.is_authenticated:
        feed, following = getFeed(request.user, 250)
        context['feed'] = feed
        context['following'] = following

    return render(request, 'users/feed.html', context)


