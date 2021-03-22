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

from django import http
from django.http import QueryDict
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect

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
            print(self.object)
            print(allFollowing)
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
            context['media'] = json.dumps(list(Film.objects.values('title', 'slug')[:300]))
        elif self.object.type == 'Television':
            entries =  ProfileSectionTelevisionMapping.objects.filter(profileSection=self.object.id)
            context['media'] = json.dumps(list(Television.objects.values('title', 'slug')[:300]))
        elif self.object.type == 'Video Games':
            entries = ProfileSectionVideoGameMapping.objects.filter(profileSection=self.object.id)
            context['media'] = json.dumps(list(VideoGame.objects.values('title', 'slug')[:300]))
        elif self.object.type == 'Books':
            entries = ProfileSectionBookMapping.objects.filter(profileSection=self.object.id)
            context['media'] = json.dumps(list(Book.objects.values('title', 'slug')[:300]))
        elif self.object.type == 'Web Series':
            entries = ProfileSectionWebSeriesMapping.objects.filter(profileSection=self.object.id)
            context['media'] = json.dumps(list(WebSeries.objects.values('title', 'slug')[:300]))
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

def getFeed(user, limit):
    following = UserFollows.objects.filter(userA=user)
    f = []

    for account in following:
        accountFilms = FilmRating.objects.filter(user=account.userB)
        accountTV = TelevisionRating.objects.filter(user=account.userB)
        accountVG = VideoGameRating.objects.filter(user=account.userB)
        accountBooks = BookRating.objects.filter(user=account.userB)
        accountWeb = WebSeriesRating.objects.filter(user=account.userB)
        accountRatings = list(chain(accountFilms, accountTV, accountVG, accountBooks, accountWeb))
        for ar in accountRatings:
            f.append(ar)

    feed = sorted(f, key=attrgetter('dateTime'), reverse=True)[:limit]
    return feed, following

def activityFeed(request):
    context = {}
    if request.user.is_authenticated:
        feed, following = getFeed(request.user, 250)
        context['feed'] = feed
        context['following'] = following

    return render(request, 'users/feed.html', context)

