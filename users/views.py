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
from media.views import genreRecommender, personRecommender, getFeed, getAllActivity

from django import http
from django.http import QueryDict
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect

import pandas as pd
import numpy as np
from django_pandas.io import read_frame
import matplotlib.pyplot as plt
from io import BytesIO
import base64

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

#Function-based view to render the user profile updating page.
#The @login_required decorator means the user is asked to log in if they are not authenticated.
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the userProfile.html file with the contents of the context dictionary
@login_required
def userProfile(request):
    #If a POST request (ie: if the user is updating their information)
    if request.POST:
        #Load the UserUpdate and ProfileUpdate forms with the current user's information as their initial instance
        userUpdateForm = UserUpdateForm(request.POST, instance=request.user)
        profileUpdateForm = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        #If the forms are valid upon submission, save the details and update the User and Profile records
        if userUpdateForm.is_valid() and profileUpdateForm.is_valid():
            userUpdateForm.save()
            profileUpdateForm.save()
            messages.success(request, f'Account Updated')
            return redirect('userProfile')

    #If a regular GET request, load the forms with the current user's information as their initial instance
    else:
        userUpdateForm = UserUpdateForm(instance=request.user)
        profileUpdateForm = ProfileUpdateForm(instance=request.user.profile)

    #Pass the forms to the template
    context = {
        'userUpdateForm' : userUpdateForm,
        'profileUpdateForm' : profileUpdateForm,
    }
    return render(request, 'users/userProfile.html', context)

#Class-based DetailView that handles, gathers the context for and renders a page for a particular user's list
class userList(generic.DetailView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = 'users/userList.html'

    #Method to return the user object based on the request made
    def get_object(self, queryset=None):
        return self.request.user

    #Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Retrieve all of the media items in this user's list
        context['films'] = UserListFilmMapping.objects.filter(user=self.object.id)
        context['television'] = UserListTelevisionMapping.objects.filter(user=self.object.id)
        context['videoGames'] = UserListVideoGameMapping.objects.filter(user=self.object.id)
        context['books'] = UserListBookMapping.objects.filter(user=self.object.id)
        context['webSeries'] = UserListWebSeriesMapping.objects.filter(user=self.object.id)

        #Retrieve the items in the list the user has already watched/read/played
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

#Class-based UpdateView that handles, gathers the context for and renders a page for a user's profile
class memberProfile(generic.UpdateView):
    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = 'users/memberProfileDetail.html'
    context_object_name = "memberProfile"
    fields=[]

    #Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #Retrieve all of the ratings made by the user
        filmRatings = FilmRating.objects.filter(user=self.object.id)
        televisionRatings = TelevisionRating.objects.filter(user=self.object.id)
        videoGameRatings = VideoGameRating.objects.filter(user=self.object.id)
        bookRatings = BookRating.objects.filter(user=self.object.id)
        webSeriesRatings = WebSeriesRating.objects.filter(user=self.object.id)
        ratings = sorted(list(chain(filmRatings, televisionRatings, videoGameRatings, bookRatings, webSeriesRatings)), key=attrgetter('dateTime'), reverse=True)

        #Pass the first 16 ratings to the context to be viewable on the main profile page
        context['ratings'] = ratings[:16]

        #Retrieve the profile sections the user has created for their profile
        profileSections = ProfileSection.objects.filter(profile__user=self.object.id).order_by('order')
        context['profileSections'] = profileSections

        if profileSections != None:
            for x in range(profileSections.count()):
                #Retrieve the Films, Television, Games, Books or web Series that make up the profile section
                films = ProfileSectionFilmMapping.objects.filter(profileSection__profile__user=self.object.id)\
                    .filter(profileSection__sectionName=profileSections[x].sectionName)
                television = ProfileSectionTelevisionMapping.objects.filter(profileSection__profile__user=self.object.id)\
                    .filter(profileSection__sectionName=profileSections[x].sectionName)
                videoGames = ProfileSectionVideoGameMapping.objects.filter(profileSection__profile__user=self.object.id)\
                    .filter(profileSection__sectionName=profileSections[x].sectionName)
                books = ProfileSectionBookMapping.objects.filter(profileSection__profile__user=self.object.id)\
                    .filter(profileSection__sectionName=profileSections[x].sectionName)
                webSeries = ProfileSectionWebSeriesMapping.objects.filter(profileSection__profile__user=self.object.id)\
                    .filter(profileSection__sectionName=profileSections[x].sectionName)

                #Compile these media items into the full profile section and pass to the context
                completeProfileSection = sorted(list(chain(films, television, videoGames,books, webSeries)), key=attrgetter('orderInSection'))
                context[profileSections[x].sectionName] = completeProfileSection

        #Pass the form to create a new profile section to the template
        context['newSectionForm'] = ProfileSectionForm

        #If the user is logged in
        #Retrieve the users they are following and see if this user is currently followed or not
        if self.request.user.is_authenticated:
            allFollowing = UserFollows.objects.filter(userA=self.request.user)
            isFollowing = False
            for following in allFollowing:
                if following.userB == self.object:
                    isFollowing = True
                    break
            context['inList'] = isFollowing

        return context

    #POST request handler method for this profile page
    def post(self, request, *args, **kwargs):

        #Retrieve this instance's user object
        object = self.get_object()

        #If the active user wishes to follow this user
        if request.POST.get('toggle') == "add":
            #Create a mapping between the active user and this user
            f = UserFollows(userA=request.user, userB=object)
            f.save()

        #If the active user wishes to unfollow this user
        elif request.POST.get('toggle') == "remove":
            #Remove the mapping between the active user and this user
            f = UserFollows.objects.filter(userA=request.user, userB=object)
            f.delete()

        #If the POST request is to reorder the profile sections
        elif request.POST.get('changing') == 'confirm':
            #Gather all of the profile sections from the POST request
            entries = QueryDict(request.POST.get('content'))
            #Enumerate the sections and reorder them by setting their 'order' field to their index in the loop
            for index, entry_id in enumerate(entries.getlist('section[]')):
                entry = ProfileSection.objects.get(id=entry_id)
                entry.order = index
                entry.save()
            #Redirect to the user profile page with the changes applied in real time without a refresh
            return http.HttpResponseRedirect('/user/' + object.username)

        #Otherwise, the POST request is to create a new profile section
        else:
            #Retrieve the name and media type of the new section
            newSectionName = request.POST.get('name')
            newSectionType = request.POST.get('type')
            #Create the record and save it to the database
            s = ProfileSection(profile=object.profile, sectionName=newSectionName, type=newSectionType)
            s.save()
        #Redirect to the user profile page with the changes applied in real time without a refresh
        return http.HttpResponseRedirect('/user/' + object.username)

#Class-based UpdateView that handles, gathers the context for and renders a page for a user's detailed ratings
#(extends the memberProfile UpdateView)
class memberProfileActivity(memberProfile):
    template_name = 'users/memberProfileActivityDetail.html'

#Class-based UpdateView that handles, gathers the context for and renders a page for a particular profile section
class profileSection(generic.UpdateView):
    model = ProfileSection
    slug_field = "slug"
    slug_url_kwarg = "slug"
    template_name = 'users/profileSectionEdit.html'
    context_object_name = "profileSection"
    fields = []

    #Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entries = []
        #Retrieve the entries of the profile section
        #Serialise the Titles and Slugs of potential media items to add into JSON to be passed to the template
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
        #Retrieve the current ProfileSection object and the user to whom the profile section belongs
        object = self.get_object()
        username = object.profile.user.username

        #If the name of the profile section is being changed
        if request.POST.get('newName') != None:
            newName = request.POST.get('newName')
            object.sectionName = newName
            object.save()
            return http.HttpResponseRedirect('/profile-section/' + object.slug)

        #If a new item is being added to the profile section
        elif request.POST.get('addMedia') != None:
            get = request.POST.get('addMedia')
            spl = get.split('/')
            #Retrieve the media item's slugfield (after the final slash in the POST request)
            mediaSlug = spl[len(spl)-1]

            #Retrieve the film object to be added and add it to the end of the section, saving the new record
            if object.type == "Films":
                getFilm = Film.objects.filter(slug=mediaSlug)[0]
                sectionLength = 0
                #Retrieve the number of items (length) of the profile section
                for psfm in ProfileSectionFilmMapping.objects.filter(profileSection=object):
                    sectionLength += 1
                #Save this new mapping record, specifying its 'orderInSection' to be the length of the section + 1 (the new end)
                newMap = ProfileSectionFilmMapping(film=getFilm, profileSection=object, orderInSection=sectionLength+1)
                newMap.save()

            #Retrieve the television object to be added and add it to the end of the section, saving the new record
            elif object.type == "Television":
                getTV = Television.objects.filter(slug=mediaSlug)[0]
                sectionLength = 0
                for pstm in ProfileSectionFilmMapping.objects.filter(profileSection=object):
                    sectionLength += 1
                newMap = ProfileSectionTelevisionMapping(television=getTV, profileSection=object, orderInSection=sectionLength + 1)
                newMap.save()

            #Retrieve the video game object to be added and add it to the end of the section, saving the new record
            elif object.type == "Video Games":
                getVG = VideoGame.objects.filter(slug=mediaSlug)[0]
                sectionLength = 0
                for psvgm in ProfileSectionVideoGameMapping.objects.filter(profileSection=object):
                    sectionLength += 1
                newMap = ProfileSectionVideoGameMapping(videoGame=getVG, profileSection=object, orderInSection=sectionLength + 1)
                newMap.save()

            #Retrieve the book object to be added and add it to the end of the section, saving the new record
            elif object.type == "Books":
                getB = Book.objects.filter(slug=mediaSlug)[0]
                sectionLength = 0
                for psbm in ProfileSectionBookMapping.objects.filter(profileSection=object):
                    sectionLength += 1
                newMap = ProfileSectionBookMapping(book=getB, profileSection=object, orderInSection=sectionLength + 1)
                newMap.save()

            #Retrieve the web series object to be added and add it to the end of the section, saving the new record
            elif object.type == "Web Series":
                getWS = WebSeries.objects.filter(slug=mediaSlug)[0]
                sectionLength = 0
                for pswsm in ProfileSectionWebSeriesMapping.objects.all():
                    if pswsm.profileSection == object:
                        sectionLength += 1
                newMap = ProfileSectionWebSeriesMapping(webSeries=getWS, profileSection=object, orderInSection=sectionLength + 1)
                newMap.save()
            return http.HttpResponseRedirect('/profile-section/' + object.slug)

        #If an item is being removed from the profile section
        elif request.POST.get('removeMedia') != None:
            get = request.POST.get('removeMedia')
            #If the first character is 'f', the film matching the POST request is removed
            if get[0] == 'f':
                getFilm = Film.objects.filter(slug=get[2:])[0]
                getMap = ProfileSectionFilmMapping.objects.filter(profileSection=object, film=getFilm)[0]
                getMap.delete()
            # If the first character is 't', the television series matching the POST request is removed
            if get[0] == 't':
                getTV = Television.objects.filter(slug=get[2:])[0]
                getMap = ProfileSectionTelevisionMapping.objects.filter(profileSection=object, television=getTV)[0]
                getMap.delete()
            # If the first character is 'v', the video game matching the POST request is removed
            if get[0] == 'v':
                getVG = VideoGame.objects.filter(slug=get[2:])[0]
                getMap = ProfileSectionVideoGameMapping.objects.filter(profileSection=object, videoGame=getVG)[0]
                getMap.delete()
            # If the first character is 'b', the book matching the POST request is removed
            if get[0] == 'b':
                getB = Book.objects.filter(slug=get[2:])[0]
                getMap = ProfileSectionBookMapping.objects.filter(profileSection=object, book=getB)[0]
                getMap.delete()
            # If the first character is 'w', the web series matching the POST request is removed
            if get[0] == 'w':
                getWS = WebSeries.objects.filter(slug=get[2:])[0]
                getMap = ProfileSectionWebSeriesMapping.objects.filter(profileSection=object, webSeries=getWS)[0]
                getMap.delete()
            #Redirect to the same profile section editing page with no refresh required
            return http.HttpResponseRedirect('/profile-section/' + object.slug)

        #If the order of the items in the profile section is being changed
        elif request.POST.get('changing') == 'confirm':
            entries = QueryDict(request.POST.get('content'))
            #Enumerate the items in the section and reorder them by setting the orderInSection to the index in the loop
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
            # Redirect to the same profile section editing page with no refresh required
            return http.HttpResponseRedirect('/profile-section/' + object.slug)

        #If the profile section is to be deleted
        elif request.POST.get('delete') == 'confirm':
            #Delete the profile section from the database
            thisSection = ProfileSection.objects.filter(id=object.id)
            thisSection.delete()
            url = "/user/"+username
            #Redirect to the user's profile page
            return redirect(url)

#Function to calculate statistics and draw a graph of a particular user's ratings of a specific media type
def userRatingStats(mediaType, user):
    #Create a Pandas Dataframe and populate it with the ratings of the type of media
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

    #Create a matplotlib histogram figure with the 'rating' column of the dataframe
    fig, ax = plt.subplots(1, 1, figsize=(3,1.5))
    ax.hist(df['rating'], rwidth=0.9)

    #Set background colour to blend in with the background of the containers on the front-end
    ax.set_facecolor('#323238')

    #Manually set labels to align with possible ratings
    rects = ax.patches
    labels = ['.5', '1', '1.5', '2', '2.5', '3', '3.5', '4', '4.5', '5']
    #for i in rects:
    #    labels.append(int(i.get_height()))

    #Iterate through the rectangles and their labels
    largest = 0
    for rect, label in zip(rects, labels):
        height = rect.get_height()
        #Find the height of the largest rectangle
        if height > largest:
            largest = height
        #Set the rectangle's colour to green
        rect.set_facecolor('#0CA06B')

    #Set the rectangles' minimum height to be at least 10% of the tallest rectangle
    for rect, label in zip(rects, labels):
        if rect.get_height() < largest*0.1:
            rect.set_height(largest*0.1)

    #Create a bytes buffer to save the figure and draw it on the front-end
    buffer = BytesIO()
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    #Set bounding box to tight and -0.1 inches removes borders and white outlines
    plt.savefig(buffer, format='png', bbox_inches = 'tight', pad_inches = -0.1)
    buffer.seek(0)
    #Retrieve the image of the plot and close the buffer
    image_png = buffer.getvalue()
    buffer.close()

    #Decode the image to allow it to be send through the returned dictionary to the front-end
    graphic = base64.b64encode(image_png)
    graphic = graphic.decode('utf-8')

    #Return the media type, count, mean, mode, standard deviation and histogram in a combined dictionary
    return { 'mediaType':mediaType,
             'Number of Ratings':df['rating'].count(),
             'Mean Rating':str(df['rating'].mean())[:4],
             'Mode Rating':str(df['rating'].mode())[3:-17],
             'Rating Standard Deviation':str(df['rating'].std())[:4],
             'hist':graphic }

#Class-based UpdateView that handles, gathers the context for and renders a page for a user's ratings statistics
class memberProfileStats(memberProfileActivity):
    template_name = 'users/memberProfileStatsDetail.html'

    #Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #Call the userRatingsStats function 5 times, once per media type
        context['stats'] = [userRatingStats('Films', self.object.id),
                            userRatingStats('Television', self.object.id),
                            userRatingStats('Video Games', self.object.id),
                            userRatingStats('Books', self.object.id),
                            userRatingStats('Web Series', self.object.id)]

        return context

#Function-based view to render the page for the activity feed from a particular user's followed profiles
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the feed.html file with the contents of the context dictionary
def activityFeed(request):
    context = {}
    #If the user is logged in, call the getFeed function to find the 250 most recent items rated by followed users
    if request.user.is_authenticated:
        feed, following = getFeed(request.user, 250)
        context['feed'] = feed
        context['following'] = following

    return render(request, 'users/feed.html', context)


