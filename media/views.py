import csv, io
import itertools
import operator
from itertools import chain
from operator import attrgetter
import locale
import collections

from django import http
from django.contrib import messages
from datetime import datetime, date
import time

from django.shortcuts import render, redirect
from django.views import generic
from django.db.models import Q
from .models import *
from users.models import *
from users.views import getFeed, getAllActivity

from .forms import *
from django.db.models import Count

import requests, json, datetime, re
from django.core.files import File

from django.core.paginator import Paginator, EmptyPage
from django.db.models.functions import Length
from .filters import *

def addUsers():
    with open("D:/MediaDB Datasets/movielensSmall/users.csv", 'r') as users:
        userData = csv.reader(users)

        for row in userData:
            print("Creating - ", row[1])
            user = User.objects.create_user(username=row[1], email=row[3], password=row[2])
            print("Created - ", row[1])

def addFilmRatings():
    ratingsFile = open("D:/MediaDB Datasets/movielensSmall/ratings.csv", "rt")
    ratingsData = csv.reader(ratingsFile)

    people = Person.objects.all()
    genres = Genre.objects.all()
    films = Film.objects.all()

    filmTitles = []
    for film in films:
        filmTitles.append(film.title)

    genreTitles = []
    for g in genres:
        genreTitles.append(g.title)

    peopleNames = []
    for p in people:
        peopleNames.append(p.getFullName())

    knownIDs = {}

    badCharsTitles = ['?', '/', '#', '!', '"', '<', '>', '[', ']', '{', '}', '@']
    badCharsPeople = ['?', '/', '#', '!', '"', '<', '>', '[', ']', '{', '}', '(', ')', ':', ';', '@']

    for row in ratingsData:
        #print(row)
        #row=row[0].split('\t')

        userID = row[0]
        imdbID = str(row[2])
        ratingScore = row[3]

        #Add 0s to make all IDs same length
        while len(imdbID) < 8:
            imdbID = "0" + imdbID

        #Don't make new request if possible
        if imdbID in knownIDs:
            title = knownIDs[imdbID]

        #Making new request
        else:
            resp = requests.get("http://www.omdbapi.com/?i=tt" + imdbID + "&apikey=5cd5955c")
            data = json.loads(resp.text)
            title = data['Title']

            if any(badChar in title for badChar in badCharsTitles):
                print("--------------------------------------------------------------------------------------")
                print("Skipped Film: ", title)
                continue

            knownIDs[imdbID] = title #Adding to knownIDs

            #If not in database already, add new film
            if title not in filmTitles:
                filmTitles.append(title)
                print("Adding new film:", title)

                try:
                    datetime.datetime.strptime(data['Released'], '%d %b %Y').strftime('%Y-%m-%d')
                except ValueError:
                    continue

                f = Film(
                    title=data['Title'],
                    release=datetime.datetime.strptime(data['Released'], '%d %b %Y').strftime('%Y-%m-%d'),
                    length=data['Runtime'][:-4],
                    synopsis=data['Plot'],
                    rating=data['Rated'],
                )

                #Getting poster data from API request, saving to local temp file and storing in Film Model Object
                img_data = requests.get(data['Poster']).content
                img_name = data['Title'] + "-" + str(data['Year']) + ".jpg"
                with open("D:/MediaDB Datasets/postersTemp/"+img_name, 'wb') as handler:
                    handler.write(img_data)

                f.poster.save(img_name, File(open("D:/MediaDB Datasets/postersTemp/"+img_name, "rb")))
                f.save()

                #Adding Genres
                genres = data['Genre'].split(', ')
                for genre in genres:
                    if genre not in genreTitles:
                        newGenre = Genre(title=genre)
                        newGenre.save()
                        genreTitles.append(newGenre)

                    getGenre = Genre.objects.filter(title=genre)[0]
                    fgm = FilmGenreMapping(film=f, genre=getGenre)
                    fgm.save()

                #Adding Directors
                directors = data['Director'].split(', ')
                for director in directors:

                    #Removing parantheses or credits from names
                    firstLastNames = re.sub(r" ?\([^)]+\)", "", director)

                    if firstLastNames == "N/A":
                        continue

                    if any(badChar in firstLastNames for badChar in badCharsPeople):
                        print("--------------------------------------------------------------------------------------")
                        print("Skipped Person: ", firstLastNames)
                        continue

                    if firstLastNames not in peopleNames:
                        print("Adding new person:", firstLastNames)
                        peopleNames.append(firstLastNames)
                        newPerson = Person()
                        firstLastNames = firstLastNames.split()
                        newPerson.firstName = firstLastNames[0]
                        if len(firstLastNames) > 1:
                            combinedSurname = ""
                            for name in firstLastNames[1:]:
                                combinedSurname += name + " "
                            newPerson.surname = combinedSurname[:-1]
                        newPerson.save()
                        thisDirector = newPerson
                    else:
                        print("Getting Existing Director: ", firstLastNames)
                        firstLastNames = firstLastNames.split(" ", 1) #Only Separating First Name Out
                        thisDirector = Person.objects.filter(firstName=firstLastNames[0], surname=firstLastNames[1])[0]

                    thisFilm = Film.objects.filter(title=title)[0]
                    directorRole = PersonRole.objects.filter(id=2)[0]

                    #If mapping doesn't already exist
                    query = FilmPersonMapping.objects.filter(person=thisDirector, film=thisFilm, role=directorRole)
                    if not query:
                        fpm = FilmPersonMapping(person=thisDirector, film=thisFilm, role=directorRole)
                        fpm.save()
                    else:
                        print(thisDirector.getFullName(), "is already tied to", thisFilm, "in this role")

                # Adding Writers
                writers = data['Writer'].split(', ')
                for writer in writers:

                    # Removing parantheses or credits from names
                    firstLastNames = re.sub(r" ?\([^)]+\)", "", writer)

                    if firstLastNames == "N/A":
                        continue

                    if any(badChar in firstLastNames for badChar in badCharsPeople):
                        print("--------------------------------------------------------------------------------------")
                        print("Skipped Person: ", firstLastNames)
                        continue

                    if firstLastNames not in peopleNames:
                        print("Adding new person:", firstLastNames)
                        peopleNames.append(firstLastNames)
                        newPerson = Person()
                        firstLastNames = firstLastNames.split()
                        newPerson.firstName = firstLastNames[0]
                        if len(firstLastNames) > 1:
                            combinedSurname = ""
                            for name in firstLastNames[1:]:
                                combinedSurname += name + " "
                            newPerson.surname = combinedSurname[:-1]
                        newPerson.save()
                        thisWriter = newPerson
                    else:
                        print("Getting Existing Writer: ", firstLastNames)
                        firstLastNames = firstLastNames.split(" ", 1) #Only Separating First Name Out
                        thisWriter = Person.objects.filter(firstName=firstLastNames[0], surname=firstLastNames[1])[0]

                    thisFilm = Film.objects.filter(title=title)[0]
                    writerRole = PersonRole.objects.filter(id=3)[0]

                    #If mapping doesn't already exist
                    query = FilmPersonMapping.objects.filter(person=thisWriter, film=thisFilm, role=writerRole)
                    if not query:
                        fpm = FilmPersonMapping(person=thisWriter, film=thisFilm, role=writerRole)
                        fpm.save()
                    else:
                        print(thisWriter.getFullName(), "is already tied to", thisFilm, "in this role")

                # Adding Actors
                actors = data['Actors'].split(', ')
                for actor in actors:

                    #Removing parantheses or credits from names
                    firstLastNames = re.sub(r" ?\([^)]+\)", "", actor)

                    if firstLastNames == "N/A":
                        continue

                    if any(badChar in firstLastNames for badChar in badCharsPeople):
                        print("--------------------------------------------------------------------------------------")
                        print("Skipped Person: ", firstLastNames)
                        continue

                    if firstLastNames not in peopleNames:
                        print("Adding new person:", firstLastNames)
                        peopleNames.append(firstLastNames)
                        newPerson = Person()
                        firstLastNames = firstLastNames.split()
                        newPerson.firstName = firstLastNames[0]
                        if len(firstLastNames) > 1:
                            combinedSurname = ""
                            for name in firstLastNames[1:]:
                                combinedSurname += name + " "
                            newPerson.surname = combinedSurname[:-1]
                        newPerson.save()
                        thisActor = newPerson
                    else:
                        print("Getting Existing Actor: ", firstLastNames)
                        firstLastNames = firstLastNames.split(" ", 1)  # Only Separating First Name Out
                        thisActor = Person.objects.filter(firstName=firstLastNames[0], surname=firstLastNames[1])[0]
                        print(thisActor)

                    thisFilm = Film.objects.filter(title=title)[0]
                    actorRole = PersonRole.objects.filter(id=1)[0]

                    # If mapping doesn't already exist
                    query = FilmPersonMapping.objects.filter(person=thisActor, film=thisFilm, role=actorRole)
                    if not query:
                        fpm = FilmPersonMapping(person=thisActor, film=thisFilm, role=actorRole)
                        fpm.save()
                    else:
                        print(thisActor.getFullName(), "is already tied to", thisFilm, "in this role")


        #Add Rating
        thisFilm = Film.objects.filter(title=title)[0]
        currentUser = User.objects.filter(id=userID)[0]
        r = FilmRating(film=thisFilm, user=currentUser, rating=ratingScore)
        r.save()

                        #eg   Film     HighestRatedFilms   50       100       True

def recalculateHighestRated(mediaType, highestRatingType, minRatings, quantity, reverse):

    top = highestRatingType.objects.all()
    for t in top:
        t.delete()

    media = mediaType.objects.all()
    ratingsDict = {}

    for m in media:
        if mediaType == Film:
            ratings = FilmRating.objects.filter(film=m)
        elif mediaType == Television:
            ratings = TelevisionRating.objects.filter(television=m)
        elif mediaType == VideoGame:
            ratings = VideoGameRating.objects.filter(videoGame=m)
        elif mediaType == Book:
            ratings = BookRating.objects.filter(book=m)
        elif mediaType == WebSeries:
            ratings = WebSeriesRating.objects.filter(webSeries=m)

        ratingsCount = ratings.count()
        if ratingsCount >= minRatings:
            ratingSum = 0
            for rating in ratings:
                ratingSum += float(rating.rating / 2)
            ratingAverage = (ratingSum / ratingsCount)
            average2DP = "{:.1f}".format(ratingAverage)
            ratingsDict[m] = average2DP

    #Anonymous function takes x and returns float(x[1]) (ie: the score as a float), used in the key parameter to sort dict
    sortedRatings = dict(sorted(ratingsDict.items(), key=lambda x: float(x[1]), reverse=reverse))

    highestRated = dict(itertools.islice(sortedRatings.items(), quantity))

    count=1
    for hr in highestRated:
        highestRatingType(media=hr, rating=highestRated[hr], rank=count).save()
        count += 1

def getHighestRated(type, quantity):
    if type == Film:
        return HighestRatedFilms.objects.all().order_by('rank')[:quantity]
    if type == Television:
        return HighestRatedTelevision.objects.all().order_by('rank')[:quantity]
    if type == VideoGame:
        return HighestRatedVideoGames.objects.all().order_by('rank')[:quantity]
    if type == Book:
        return HighestRatedBooks.objects.all().order_by('rank')[:quantity]
    return HighestRatedWebSeries.objects.all().order_by('rank')[:quantity]

def calculateTopGrossing(quantity):
    topGrossing = Film.objects.all().order_by('-boxOffice')[:quantity]
    filmGrossingDict = {}

    for f in topGrossing:
        gross = float('{:.3g}'.format(f.boxOffice))
        magnitude = 0
        symbols = ['', 'K', 'M', 'B', 'T']
        while abs(gross) >= 1000:
            magnitude += 1
            gross /= 1000.0
        filmGrossingDict[f] = '$' + '{}{}'.format('{:.3f}'.format(gross).rstrip('0'), symbols[magnitude])

    return filmGrossingDict

def findDulplicateTitles():

    #repeated_names = Application.objects.values('school_name', 'category').annotate(Count('id')).order_by().filter(
    #    id__count__gt=0)  # <--- gt 0 will get all the objects having occurred in DB i.e is greater than 0

    repeatedTitles = Film.objects.values('title').annotate(Count('id')).order_by().filter(id__count__gt=1)

    return repeatedTitles

def mediaPagePostRequests(self, request, *args, **kwargs):
    object = self.get_object()
    print(type(object))

    if self.request.user.is_authenticated:

        #POST Request: Adding/Removing from List
        if request.POST['type'] == "listToggle":
            toggle = request.POST['toggle']
            #Adding Media to List
            if toggle == "add":
                if isinstance(object, Film):
                    l = UserListFilmMapping(user=self.request.user, film=object)
                elif isinstance(object, Television):
                    l = UserListTelevisionMapping(user=self.request.user, television=object)
                elif isinstance(object, VideoGame):
                    l = UserListVideoGameMapping(user=self.request.user, videoGame=object)
                elif isinstance(object, Book):
                    l = UserListBookMapping(user=self.request.user, book=object)
                elif isinstance(object, WebSeries):
                    l = UserListWebSeriesMapping(user=self.request.user, webSeries=object)
                l.save()
            else:
                #Removing Media from List
                if isinstance(object, Film):
                    UserListFilmMapping.objects.filter(user=self.request.user, film=object.id).delete()
                elif isinstance(object, Television):
                    UserListTelevisionMapping.objects.filter(user=self.request.user, television=object.id).delete()
                elif isinstance(object, VideoGame):
                    UserListVideoGameMapping.objects.filter(user=self.request.user, videoGame=object.id).delete()
                elif isinstance(object, Book):
                    UserListBookMapping.objects.filter(user=self.request.user, book=object.id).delete()
                elif isinstance(object, WebSeries):
                    UserListWebSeriesMapping.objects.filter(user=self.request.user, webSeries=object.id).delete()

        #POST Request: Adding/Changing a Rating
        elif request.POST['type'] == "rating":

            #Attempt to retrieve a rating made by that user for that
            newRating = float(request.POST['nr'])
            if isinstance(object, Film):
                r = FilmRating.objects.filter(user=self.request.user, film=object.id).first()
            elif isinstance(object, Television):
                r = TelevisionRating.objects.filter(user=self.request.user, television=object.id).first()
            elif isinstance(object, VideoGame):
                r = VideoGameRating.objects.filter(user=self.request.user, videoGame=object.id).first()
            elif isinstance(object, Book):
                r = BookRating.objects.filter(user=self.request.user, book=object.id).first()
            elif isinstance(object, WebSeries):
                r = WebSeriesRating.objects.filter(user=self.request.user, webSeries=object.id).first()

            # If Updating a Rating
            if r is not None:
                r.rating = newRating
                r.dateTime = datetime.datetime.now()
                r.save()
            # If Creating a New Rating
            else:
                if isinstance(object, Film):
                    rating = FilmRating(user=self.request.user, film=object, rating=newRating)
                elif isinstance(object, Television):
                    rating = TelevisionRating(user=self.request.user, television=object, rating=newRating)
                elif isinstance(object, VideoGame):
                    rating = VideoGameRating(user=self.request.user, videoGame=object, rating=newRating)
                elif isinstance(object, Book):
                    rating = BookRating(user=self.request.user, book=object, rating=newRating)
                elif isinstance(object, WebSeries):
                    rating = WebSeriesRating(user=self.request.user, webSeries=object, rating=newRating)
                rating.save()

        #POST Request: Review
        else:
            newReview = request.POST['newReview']
            print(newReview)
            if isinstance(object, Film):
                r = FilmRating.objects.filter(user=self.request.user, film=object.id).first()
            elif isinstance(object, Television):
                r = TelevisionRating.objects.filter(user=self.request.user, television=object.id).first()
            elif isinstance(object, VideoGame):
                r = VideoGameRating.objects.filter(user=self.request.user, videoGame=object.id).first()
            elif isinstance(object, Book):
                r = BookRating.objects.filter(user=self.request.user, book=object.id).first()
            elif isinstance(object, WebSeries):
                r = WebSeriesRating.objects.filter(user=self.request.user, webSeries=object.id).first()

            r.review = newReview
            r.dateTime = datetime.datetime.now()
            r.save()

    return super(FilmDetailView, self).post(request, *args, **kwargs)

def dataSources(request):
    context = {}
    return render(request, "media/dataSources.html", context)

def csvUpload(request):
    prompt = {
        'format':'Format should be Title, Release, Rating, Synopsis, Length, Budget, BoxOffice, PosterFilePath'
    }

    if request.method == "GET":
        return render(request, 'media/csvUpload.html', prompt)

    csv_file = request.FILES['filmsFile']

    if not csv_file.name.endswith('.csv'):
        messages.error(request, 'This is not a csv file')

    data_set = csv_file.read().decode('ISO-8859-1')
    io_string = io.StringIO(data_set)
    next(io_string)

    for column in csv.reader(io_string, delimiter=','):
        _, created = Film.objects.update_or_create(
            title = column[0],
            release = column[1],
            rating = column[2],
            synopsis = column[3],
            length = column[4],
            budget = column[5],
            boxOffice = column[6],
        )

    context = {}

    return render(request, 'media/csvUpload.html', context)

def topRatedUnseen(user):
    userFilmRatings = FilmRating.objects.filter(user=user)
    topRated = getHighestRated(Film, 250)
    seen = []
    unseen = []
    for rating in userFilmRatings:
        seen.append(rating.film)
    for tr in topRated:
        if tr.media not in seen:
            unseen.append(tr)
    return unseen[:500]

def actorScores(user):
    userFilmRatings = FilmRating.objects.filter(user=user)
    actorScores = {}
    directorScores = {}
    writerScores = {}
    actorAverages = {}

    for ufr in userFilmRatings:
        film = ufr.film
        rating = ufr.rating
        people = FilmPersonMapping.objects.filter(film=film)
        actors = people.filter(role=1)
        directors = people.filter(role=2)
        writers = people.filter(role=3)

        if actors:
            for a in actors:
                actor = a.person.getFullName()
                if actor not in actorScores:
                    actorScores[actor] = []
                    actorScores[actor].append(rating)
                else:
                    actorScores[actor].append(rating)

            for actorScore in actorScores:
                sum = 0
                for score in actorScores[actorScore]:
                    sum += score
                average = sum/len(actorScores[actorScore])
                actorAverages[actorScore] = average

    return actorAverages

def genreScores(user):
    userFilmRatings = FilmRating.objects.filter(user=user)
    genreScores = {}
    genreAverages = {}

    for ufr in userFilmRatings:
        film = ufr.film
        rating = ufr.rating
        genres = FilmGenreMapping.objects.filter(film=film)

        if genres:
            for g in genres:
                genre = g.genre.title
                if genre not in genreScores:
                    genreScores[genre] = []
                    genreScores[genre].append(rating)
                else:
                    genreScores[genre].append(rating)

            for gs in genreScores:
                sum = 0
                for score in genreScores[gs]:
                    sum += score
                average = sum/len(genreScores[gs])
                genreAverages[gs] = average

    return genreAverages

def genreBasedRecommender(user):
    genresScores = genreScores(user)
    trUnseen = topRatedUnseen(user)
    filmScores = {}

    for unseen in trUnseen:
        score = 0
        filmGenres = FilmGenreMapping.objects.filter(film=unseen.media)
        for genre in filmGenres:
            if genre.genre.title in genresScores:
                score += genresScores[genre.genre.title]
        if filmGenres.count() > 1:
            score = score / filmGenres.count()
        score = score/2
        filmScores[unseen.media] = "{:.1f}".format(score)

    #Sort films by highest genre score
    sort = dict(sorted(filmScores.items(), key=lambda item: item[1], reverse=True))

    #Retrieve only the top 100 highest predicted ratings
    recommendations = {}
    iterator = iter(sort.items())
    for i in range(100):
        film = next(iterator)[0]
        recommendations[film] = sort[film]

    return recommendations, genresScores

def actorBasedRecommender(user):
    actorsScores = actorScores(user)
    trUnseen = topRatedUnseen(user)
    filmScores = {}

    for unseen in trUnseen:
        score = 0
        filmPeople = FilmPersonMapping.objects.filter(film=unseen.media)
        filmActors = filmPeople.filter(role=1)

        for actor in filmActors:
            if actor.person.getFullName() in actorsScores:
                score += actorsScores[actor.person.getFullName()]
        if filmActors.count() > 1:
            score = score / filmActors.count()
        score = score / 2
        filmScores[unseen.media] = "{:.1f}".format(score)

    # Sort films by highest genre score
    sort = dict(sorted(filmScores.items(), key=lambda item: item[1], reverse=True))

    # Retrieve only the top 100 highest predicted ratings
    recommendations = {}
    iterator = iter(sort.items())
    for i in range(100):
        film = next(iterator)[0]
        recommendations[film] = sort[film]

    return recommendations, actorsScores

def recommendationsTestingPage(request):
    context = {}
    if request.user.is_authenticated:
        #context['recommendationsV1'] = topRatedUnseen(request.user)
        genreRecommendations, genreScores = genreBasedRecommender(request.user)
        context['genreRecommendations'] = genreRecommendations
        context['genreScores'] = genreScores

        actorRecommendations, actorScores = actorBasedRecommender(request.user)
        context['actorRecommendations'] = actorRecommendations
        context['actorScores'] = actorScores

    return render(request, 'media/recommendations.html', context)

def getUpcomingTitles(f, tv, vg, b, ws):
    upcoming = []
    if f:
        for film in Film.objects.filter(release__year=datetime.datetime.now().year)[:50]:
            if film.release > date.today():
                upcoming.append(film)

    if tv:
        for television in Television.objects.filter(release__year=datetime.datetime.now().year)[:50]:
            if television.release > date.today():
                upcoming.append(television)

    if vg:
        for videoGame in VideoGame.objects.filter(release__year=datetime.datetime.now().year)[:50]:
            if videoGame.release > date.today():
                upcoming.append(videoGame)

    if b:
        for book in Book.objects.filter(release__year=datetime.datetime.now().year)[:50]:
            if book.release > date.today():
                upcoming.append(book)

    if ws:
        for webSeries in WebSeries.objects.filter(release__year=datetime.datetime.now().year)[:50]:
            if webSeries.release > date.today():
                upcoming.append(webSeries)

    return sorted(upcoming, key=attrgetter('release'))

def home(request):

    context = {
        'upcoming':getUpcomingTitles(f=True, tv=True, vg=True, b=True, ws=True),
        'longestRunningTV':Television.objects.all().order_by('-episodes')[:16],
        'books':Book.objects.all()[:30],
        'webseries':WebSeries.objects.all()[:30],
        'bornToday': Person.objects.all().filter(DoB__day=date.today().day).filter(DoB__month=date.today().month),
        'highestRatedFilms':getHighestRated(Film, 30),
        'topGrossing':calculateTopGrossing(16),
    }

    feed, following = getFeed(request.user, 16)
    if following.count() < 1 or not request.user.is_authenticated:
        context['feed'] = getAllActivity(request.user, 16)
    else:
        context['feed'] = feed
        context['personal'] = True

    return render(request, 'media/home.html', context)

import collections

def calendar(request):
    monthList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    months = {}
    num = 0

    for p in Person.objects.all().order_by('DoB__month'):
        if p.DoB != None:
            num += 1
            date = str(monthList[p.DoB.month - 1])
            if date in months:
                months[date].append(p)
            else:
                months[date] = []
                months[date].append(p)

    for month in months:
        print(months[month])
        monthSort = sorted(months[month], key=attrgetter('DoB.day'))
        months[month] = monthSort

    context = {
        'num':num,
        'counts':findDulplicateTitles(),
        'people':months
    }
    return render (request, 'media/calendar.html', context)

def addVideoGameData():
    badCharsTitles = ['?', '/', '#', '"', '<', '>', '[', ']', '{', '}', '@']

    with open("D:\MediaDB Datasets\gamesData.json", "r", encoding="utf8") as f:
        data = json.loads(f.read())

    for franchise in data:
        print("--------- Found:", franchise['name'], "-----------------------------")

        if 'games' not in franchise:
            continue

        for game in franchise['games']:
            videoGames = []
            qs = VideoGame.objects.all()
            for vg in qs:
                videoGames.append(vg.slug)

            title = game['name']

            if any(badChar in title for badChar in badCharsTitles):
                print("--- Skipped Game:", title, ". Invalid Characters")
                continue

            if 'first_release_date' not in game:
                print("--- Skipped Game:", title, ". Requires Release Date" )
                continue
            else:
                dateConv = time.strftime('%Y-%m-%d', time.localtime(game['first_release_date']))

            slug = slugify(title + "-" + str(dateConv))

            #Making New Game
            if slug not in videoGames:
                print("--- Adding Game:", title)
                newGame = VideoGame()
                newGame.title = title
                newGame.release = dateConv
                newGame.save()

            #Getting Game (whether it is newly made or not)
            getGame = VideoGame.objects.filter(slug=slug)[0]

            #Adding synopsis if there isn't one already
            if not getGame.synopsis:
                if 'summary' in game:
                    if len(game['summary']) < 1000:
                        print("Adding synopsis")
                        getGame.synopsis = game['summary']
                        getGame.save()

            #Adding poster if there isn't one already
            if bool(getGame.poster) == False:
                print("No Poster on this object")
                if 'cover' in game:
                    print("Adding poster")
                    coverURL = game['cover']['url']
                    img = coverURL.rsplit('/', 1)[-1]
                    newURL = "https://images.igdb.com/igdb/image/upload/t_cover_big/" + img

                    img_data = requests.get(newURL).content
                    img_name = slugify(title + "-" + str(dateConv)) + ".jpg"
                    with open("D:/MediaDB Datasets/gamePostersTemp/" + img_name, 'wb') as handler:
                        handler.write(img_data)

                    getGame.poster.save(img_name, File(open("D:/MediaDB Datasets/gamePostersTemp/" + img_name, "rb")))
                    getGame.save()

            if 'genres' in game:
                print("Adding genres")
                for genre in game['genres']:
                    getGameGenres = []
                    for gg in VideoGameGenreMapping.objects.filter(videoGame=getGame):
                        getGameGenres.append(gg.genre.title)
                    if genre['name'] not in getGameGenres:
                        #Make List of All Video Game Genres
                        allGameGenres = []
                        qs = VideoGameGenre.objects.all()
                        for vgg in qs:
                            allGameGenres.append(vgg.title)

                        #Create New Genre If Required
                        if genre['name'] not in allGameGenres:
                            newGameGenre = VideoGameGenre(title=genre['name'])
                            newGameGenre.save()

                        #Get Genre (whether it is old or has just been made)
                        getGenre = VideoGameGenre.objects.filter(title=genre['name'])[0]

                        #Make Mapping
                        gameGenreMap = VideoGameGenreMapping(videoGame=getGame, genre=getGenre)
                        gameGenreMap.save()

            if 'platforms' in game:
                print("Adding platforms")
                for platform in game['platforms']:
                    getGamePlatforms = []
                    for gp in VideoGameConsoleMapping.objects.filter(videoGame=getGame):
                        getGamePlatforms.append(gp.console.name)
                    if platform['name'] not in getGamePlatforms:
                        # Make List of All Video Game Genres
                        allGamePlatforms = []
                        qs = Console.objects.all()
                        for c in qs:
                            allGamePlatforms.append(c.name)
                            allGamePlatforms.append(c.shortName)

                        # Skip this console if it does not exist in the database
                        if platform['name'] not in allGamePlatforms:
                            continue

                        # Get console
                        if Console.objects.filter(name=platform['name']) != None:
                            getConsole = Console.objects.filter(name=platform['name'])[0]
                        else:
                            getConsole = Console.objects.filter(shortName=platform['name'])[0]

                        # Make Mapping
                        gameConsoleMap = VideoGameConsoleMapping(videoGame=getGame, console=getConsole)
                        gameConsoleMap.save()

            if 'involved_companies' in game:
                print("Adding companies")
                for company in game['involved_companies']:
                    getGameCompanies = []
                    for gc in VideoGameCompanyMapping.objects.filter(videoGame=getGame):
                        getGameCompanies.append(gc.company.name)
                    if company['company']['name'] not in getGameCompanies:
                        allGameCompanies = []
                        qs = Company.objects.all()
                        for c in qs:
                            allGameCompanies.append(c.name)

                        #Create new company if required
                        if company['company']['name'] not in allGameCompanies:
                            newCompany = Company(name=company['company']['name'])
                            newCompany.save()

                        #Get Company
                        getCompany = Company.objects.filter(name=company['company']['name'])[0]

                        if company['developer'] == True:
                            getDevRole = CompanyRole.objects.filter(id=4)[0]
                            gameCompanyMap = VideoGameCompanyMapping(videoGame=getGame, company=getCompany, role=getDevRole)
                            gameCompanyMap.save()
                        if company['publisher'] == True:
                            getPubRole = CompanyRole.objects.filter(id=5)[0]
                            gameCompanyMap = VideoGameCompanyMapping(videoGame=getGame, company=getCompany, role=getPubRole)
                            gameCompanyMap.save()

        print("\n")

def searchResults(request):

    #addVideoGameData()

    #recalculateHighestRated(VideoGame, HighestRatedVideoGames, minRatings=1, quantity=50, reverse=True)

    #h = getHighestRated(Television, 50)
    #for f in h:
    #    print(str(f.rank) + " - " + f.media.title + " - " + str(f.rating))

    #noposters=[]
    #for vg in Film.objects.all():
    #    if bool(vg.poster) == False:
    #        noposters.append(vg.id)
    #print(noposters)

    #subcat = VideoGameFranchiseSubcategory.objects.get(pk=145)
    #subcat2 = VideoGameFranchiseSubcategory.objects.get(pk=143)
    #subcat3 = VideoGameFranchiseSubcategory.objects.get(pk=144)

    #for g in VideoGame.objects.filter(release__range=["2000-01-01", "2020-12-25"]).order_by('release'):
    #    if 'donkey kong' in g.title.lower():
    #        if 'country' not in g.title.lower():
    #            VideoGameVideoGameFranchiseSubcategoryMapping(videoGame=g, videoGameFranchiseSubcategory=subcat, orderInFranchise=1).save()


    title_contains = request.GET.get('q')

    context = {}
    if title_contains != '' and title_contains is not None:
        people = []
        for p in Person.objects.all():
            if p.getFullName().lower().__contains__(title_contains):
              people.append(p)

        context = {
            'searchQuery':title_contains,
            'people':people,
            'franchises': Franchise.objects.all().filter(title__icontains=title_contains).order_by('id')[:20],
            'videogamefranchises': VideoGameFranchise.objects.all().filter(title__icontains=title_contains).order_by('id')[:20],
            'consoles' : Console.objects.all().filter(Q(name__icontains=title_contains) | Q(shortName__icontains=title_contains)).order_by('name')[:20],
            'films':Film.objects.all().filter(title__icontains=title_contains).order_by('id')[:20],
            'tv':Television.objects.all().filter(title__icontains=title_contains).order_by('id')[:20],
            'games':VideoGame.objects.all().filter(title__icontains=title_contains).order_by('id')[:75],
            'books':Book.objects.all().filter(title__icontains=title_contains).order_by('id')[:20],
            'webseries':WebSeries.objects.all().filter(title__icontains=title_contains).order_by('id')[:20],
            'companies': Company.objects.all().filter(name__icontains=title_contains).order_by('id')[:20],
        }
    return render(request, 'media/searchResults.html', context)

def browse(request):

    films = Film.objects.all()
    #television = Television.objects.all()
    #videoGames = VideoGame.objects.all()
    #books = Book.objects.all()
    #webSeries = WebSeries.objects.all()
    #people = Person.objects.exclude(image='MissingIcon.png')
    #print(people.count())
    #allMedia = list(chain(films, television, videoGames, books, webSeries, people))

    filteredFilms = filmFilter(request.GET, queryset=films)

    paginatedFilteredFilms = Paginator(filteredFilms.qs, 90)
    page_number = request.GET.get('page', 1)
    mediaPageObject = paginatedFilteredFilms.get_page(page_number)

    context = {
        'filteredFilms' : filteredFilms,
        'mediaPageObject': mediaPageObject,
        'seenFilms' : FilmRating.objects.filter(user=request.user)
    }

    if request.user.is_authenticated:
        userRatings = FilmRating.objects.filter(user=request.user)
        seenFilms = []
        for ur in userRatings:
            seenFilms.append(ur.film)
        context['seenFilms'] = seenFilms

    return render(request, 'media/browse.html', context)

def filmHome(request):
    genres = []
    g = Genre.objects.all()
    for genre in g:
        if genre.image:
            genres.append(genre)

    context = {
        'highestRatedFilms': getHighestRated(Film, 100),
        'franchises':Franchise.objects.all(),
        'genres':genres,
        'seventies':Film.objects.all().filter(release__range=["1970-01-01", "1979-12-25"])[:30],
        'eighties': Film.objects.all().filter(release__range=["1980-01-01", "1989-12-25"])[:30],
        'nineties':Film.objects.all().filter(release__range=["1990-01-01", "1999-12-25"])[:30],
    }
    return render(request, 'media/filmHome.html', context)

def tvHome(request):
    context = {
        'highestRatedShows':getHighestRated(Television, 100),
        'shows': Television.objects.all(),
        'genres': Genre.objects.all(),
        'nineties': Television.objects.all().filter(release__range=["1990-01-01", "1999-12-25"]),
        'naughties': Television.objects.all().filter(release__range=["2000-01-01", "2009-12-25"]),
        'tens': Television.objects.all().filter(release__range=["2010-01-01", "2019-12-25"]),

    }
    return render(request, 'media/tvHome.html', context)

def gameHome(request):

    gameCompanies = []
    for vgcm in VideoGameCompanyMapping.objects.filter(role=4):
        if vgcm.company not in gameCompanies:
            if vgcm.company.image:
                gameCompanies.append(vgcm.company)
    for vgcm in VideoGameCompanyMapping.objects.filter(role=5):
        if vgcm.company not in gameCompanies:
            if vgcm.company.image:
                gameCompanies.append(vgcm.company)
    genres = []
    g = VideoGameGenre.objects.all()
    for genre in g:
        if genre.image:
            genres.append(genre)

    franchises = []
    others = []
    for vgf in VideoGameVideoGameFranchiseSubcategoryMapping.objects.all():
        if vgf.videoGameFranchiseSubcategory.parentFranchise not in franchises:
            franchises.append(vgf.videoGameFranchiseSubcategory.parentFranchise)

    context = {
        'topRated':getHighestRated(VideoGame, 20),
        'upcoming':getUpcomingTitles(f=False, tv=False, vg=True, b=False, ws=False),
        'consoles': Console.objects.all().order_by('-release'),
        'franchises':franchises,
        'genres': genres,
        'companies': gameCompanies,
    }
    return render(request, 'media/gameHome.html', context)

def bookHome(request):

    genreCounts = {}
    noGenres = []

    for v in Film.objects.all():
        genreCounts[v] = 0

    for map in FilmGenreMapping.objects.all():
        genreCounts[map.film] += 1

    for v in genreCounts:
        if genreCounts[v] == 0:
            noGenres.append(v)
    """
    for ng in noGenres:
        action = VideoGameGenre.objects.filter(id=1)[0]
        fantasy = VideoGameGenre.objects.filter(id=3)[0]
        rpg = VideoGameGenre.objects.filter(id=6)[0]
        adventure = VideoGameGenre.objects.filter(id=2)[0]
        openworld = VideoGameGenre.objects.filter(id=12)[0]
        stealth = VideoGameGenre.objects.filter(id=16)[0]
        shooter = VideoGameGenre.objects.filter(id=10)[0]
        fighting = VideoGameGenre.objects.filter(id=14)[0]
        platform = VideoGameGenre.objects.filter(id=19)[0]
        arcade = VideoGameGenre.objects.filter(id=9)[0]
        sport = VideoGameGenre.objects.filter(id=24)[0]

        map1 = VideoGameGenreMapping(videoGame=ng, genre=adventure)
        map1.save()
        map2 = VideoGameGenreMapping(videoGame=ng, genre=action)
        map2.save()
    """
    context = {
        'books':Book.objects.all(),
        'nogenres':noGenres,
    }
    return render(request, 'media/bookHome.html', context)

def webHome(request):
    context = {
        'webSeries': WebSeries.objects.all(),
    }
    return render(request, 'media/webHome.html', context)

def contributeHome(request):
    return render(request, 'media/contributeMedia.html')

def contributeMedia(request):

    filmForm = ContributeFilmForm(request.POST or None, request.FILES or None, initial={
        'title':'', 'release':'', 'rating':'', 'synopsis':'', 'length':'',
        'budget':'', 'boxOffice':'', 'posterFilePath':'', 'trailerVideoPath':''
    })

    televisionForm = ContributeTelevisionForm(request.POST or None, request.FILES or None, initial={
        'title':'', 'release':'', 'synopsis':'', 'seasons':'', 'episodes':'',
        'budget':'', 'boxOffice':'', 'posterFilePath':'', 'trailerVideoPath':''
    })

    forms = [filmForm, televisionForm]

    context = {
        'forms':forms,
    }

    if request.method == 'POST':
        if filmForm.is_valid():
            new = filmForm.save(commit=False)
            new.poster = request.FILES.get('poster')
            filmForm.save()
            messages.success(request, "Successfully added film")
            return http.HttpResponseRedirect('/contribute-media')
        if televisionForm.is_valid():
            televisionForm.save()
            messages.success(request, "Successfully added Television")
            return http.HttpResponseRedirect('/contribute-media')

    return render(request, 'media/contributeMedia.html', context)

def contributePerson(request):
    initialValues = {
        'firstName': '', 'surname':'', 'Bio':'', 'DoB':'', 'DoD':'',
    }
    form = ContributePersonForm(request.POST or None, initial=initialValues)
    context = {
        'form':form
    }

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Successfully added person")
            return http.HttpResponseRedirect('/contribute-person')

    return render(request, 'media/contributePerson.html', context)

def contributeRole(request):
    return render(request, 'media/contributeRole.html')

def contributeCompany(request):
    return render(request, 'media/contributeCompany.html')

def contributeOther(request):
    return render(request, 'media/contributeOther.html')

def AwardsHome(request):
    context = {
        'shows':AwardsShow.objects.all().order_by('-date'),
        'types':AwardType.objects.all()
    }
    return render(request, 'media/awardsHome.html', context)

def franchiseHome(request):
    context = {
        'franchises':Franchise.objects.all()
    }
    return render(request, 'media/franchisesHome.html', context)

def videoGameFranchiseHome(request):

    franchises = []
    others = []
    for vgf in VideoGameVideoGameFranchiseSubcategoryMapping.objects.all():
        if vgf.videoGameFranchiseSubcategory.parentFranchise not in franchises:
            franchises.append(vgf.videoGameFranchiseSubcategory.parentFranchise)

    context = {
        'franchises':franchises,
        'others':VideoGameFranchise.objects.all()
    }
    return render(request, 'media/gameFranchiseHome.html', context)

def topGrossing(request):

    topGrossing = {}
    for film in Film.objects.all().order_by('-boxOffice')[:100]:
        topGrossing[film] = '$' + format(film.boxOffice, ",")

    context = {
        'topGrossing':topGrossing,
    }
    return render(request, 'media/topGrossing.html', context)

def topRated(request):
    context = {
        'topRated':calculateHighestRated(type=Film, minRatings=30, quantity=100, reverse=True)
    }
    return render(request, 'media/topRated.html', context)

class AwardsShowDetail(generic.DetailView):
    model = AwardsShow
    template_name = 'media/awardShowDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        peopleImages = PersonImages.objects.filter(awardsShow=self.object.id)
        miscImages = MiscImages.objects.filter(awardsShow=self.object.id)
        if peopleImages:
            if miscImages:
                context['images'] = chain(peopleImages, miscImages)
            else:
                context['images'] = peopleImages

        else:
            if miscImages:
                context['images'] = miscImages

        context['filmNominees'] = FilmAwardMapping.objects.filter(awardsShow=self.object.id).order_by('category__categoryOrder')
        context['filmCredits'] = FilmAwardCreditMapping.objects.filter(FilmAwardMapping__awardsShow=self.object.id)

        #Determine the award categories

        categories = AwardsCategories.objects.filter(awardType=self.object.award).order_by('categoryOrder')
        context['categories'] = categories

        #Define dynamic context variables for each category for this show
        if categories != None:
            for x in range(categories.count()):
                context[categories[x].name] = FilmAwardCreditMapping.objects.filter(FilmAwardMapping__awardsShow=self.object.id).filter(FilmAwardMapping__category=categories[x])

        context['tvNominees'] = TelevisionAwardMapping.objects.filter(awardsShow=self.object.id)
        context['videogamesNominees'] = VideoGameAwardMapping.objects.filter(awardsShow=self.object.id)
        context['booksNominees'] = BookAwardMapping.objects.filter(awardsShow=self.object.id)
        context['webseriesNominees'] = WebSeriesAwardMapping.objects.filter(awardsShow=self.object.id)
        return context

class AwardsTypeDetail(generic.DetailView):
    model = AwardType
    template_name = 'media/awardTypeDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['shows'] = AwardsShow.objects.filter(award=self.object.id).order_by('-date')
        return context

class AwardsCategoryDetail(generic.DetailView):
    model = AwardsCategories
    template_name = 'media/awardCategoryDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['films'] = FilmAwardCreditMapping.objects.filter(FilmAwardMapping__category=self.object.id).filter(FilmAwardMapping__win=True)
        a = FilmAwardCreditMapping.objects.filter(FilmAwardMapping__category=self.object.id)
        print(a)
        context['television'] = TelevisionAwardCreditMapping.objects.filter(TelevisionAwardMapping__category=self.object.id).filter(TelevisionAwardMapping__win=True)
        context['videogames'] = VideoGameAwardCreditMapping.objects.filter(VideoGameAwardMapping__category=self.object.id).filter(VideoGameAwardMapping__win=True)
        context['books'] = BookAwardCreditMapping.objects.filter(BookAwardMapping__category=self.object.id).filter(BookAwardMapping__win=True)
        context['webseries'] = WebSeriesAwardCreditMapping.objects.filter(WebSeriesAwardMapping__category=self.object.id).filter(WebSeriesAwardMapping__win=True)
        return context

class PersonDetailView(generic.DetailView):
    model = Person
    slug_field, slug_url_kwarg = "slug", "slug"
    template_name = 'media/personDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        fActing = []
        for fa in FilmPersonMapping.objects.filter(person=self.object.id).filter(role=1).order_by('-film__release'):
            fActing.append(fa.film)
        tvActing = []
        for tva in TelevisionPersonMapping.objects.filter(person=self.object.id).filter(role=1).order_by('-television__release'):
            tvActing.append(tva.television)
        vgActing = []
        for vga in VideoGamePersonMapping.objects.filter(person=self.object.id).filter(role=1).order_by('-videogame__release'):
            vgActing.append(vga.videogame)
        wsActing = []
        for wsa in WebSeriesPersonMapping.objects.filter(person=self.object.id).filter(role=1).order_by('-webSeries__release'):
            wsActing.append(wsa.webSeries)
        actingAll = list(chain(fActing, tvActing, vgActing, wsActing))
        acting = sorted(actingAll, key=attrgetter('release'), reverse=True)

        fDirecting = []
        for fd in FilmPersonMapping.objects.filter(person=self.object.id).filter(role=2).order_by('-film__release'):
            fDirecting.append(fd.film)
        tvDirecting = []
        for tvd in TelevisionPersonMapping.objects.filter(person=self.object.id).filter(role=2).order_by('-television__release'):
            tvDirecting.append(tvd.television)
        vgDirecting = []
        for vgd in VideoGamePersonMapping.objects.filter(person=self.object.id).filter(role=2).order_by('-videogame__release'):
            vgDirecting.append(vgd.videogame)
        wsDirecting = []
        for wsd in WebSeriesPersonMapping.objects.filter(person=self.object.id).filter(role=2).order_by('-webSeries__release'):
            wsDirecting.append(wsd.webSeries)
        directingAll = list(chain(fDirecting, tvDirecting, vgDirecting, wsDirecting))
        directing = sorted(directingAll, key=attrgetter('release'), reverse=True)

        fWriting = []
        for fw in FilmPersonMapping.objects.filter(person=self.object.id).filter(role=3).order_by('-film__release'):
            fWriting.append(fw.film)
        tvWriting = []
        for tvw in TelevisionPersonMapping.objects.filter(person=self.object.id).filter(role=3).order_by('-television__release'):
            tvWriting.append(tvw.television)
        vgWriting = []
        for vgw in VideoGamePersonMapping.objects.filter(person=self.object.id).filter(role=3).order_by('-videogame__release'):
            vgWriting.append(vgw.videogame)
        bWriting = []
        for bw in BookPersonMapping.objects.filter(person=self.object.id).filter(role=3).order_by('-book__release'):
            bWriting.append(bw.book)
        wsWriting = []
        for wsw in WebSeriesPersonMapping.objects.filter(person=self.object.id).filter(role=3).order_by('-webSeries__release'):
            wsWriting.append(wsw.webSeries)
        writingAll = list(chain(fWriting, tvWriting, vgWriting, bWriting, wsWriting))
        writing = sorted(writingAll, key=attrgetter('release'), reverse=True)

        fProducing = []
        for fp in FilmPersonMapping.objects.filter(person=self.object.id).filter(role=6).order_by('-film__release'):
            fProducing.append(fp.film)
        tvProducing = []
        for tvp in TelevisionPersonMapping.objects.filter(person=self.object.id).filter(role=6).order_by('-television__release'):
            tvProducing.append(tvp.television)
        vgProducing = []
        for vgp in VideoGamePersonMapping.objects.filter(person=self.object.id).filter(role=6).order_by('-videogame__release'):
            vgProducing.append(vgp.videogame)
        wsProducing = []
        for wsp in WebSeriesPersonMapping.objects.filter(person=self.object.id).filter(role=6).order_by('-webSeries__release'):
            wsProducing.append(wsp.webSeries)
        producingAll = list(chain(fProducing, tvProducing, vgProducing, wsProducing))
        producing = sorted(producingAll, key=attrgetter('release'), reverse=True)

        roleOrder = {}
        if len(actingAll) > 0:
            roleOrder['Actor'] = acting
        if len(directingAll) > 0:
            roleOrder['Director'] = directing
        if len(writingAll) > 0:
            roleOrder['Writer'] = writing
        if len(producingAll) > 0:
            roleOrder['Producer'] = producing

        ordered = sorted(roleOrder.items(), key= lambda x: len(x[1]), reverse=True)
        context['roles'] = ordered

        context['images'] = PersonImages.objects.filter(person=self.object.id)
        context['nominationCount'] = FilmAwardCreditMapping.objects.filter(Person=self.object.id).count()
        context['winCount'] = FilmAwardCreditMapping.objects.filter(Person=self.object.id, FilmAwardMapping__win=True).count()
        return context

class CompanyDetailView(generic.DetailView):
    model = Company
    template_name = 'media/companyDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['consoles'] = Console.objects.filter(developer=self.object.id).order_by('-release')
        context['films'] = FilmCompanyMapping.objects.filter(company=self.object.id).order_by('film__release')
        context['television'] = TelevisionCompanyMapping.objects.filter(company=self.object.id).order_by('television__release')

        gameMappings = VideoGameCompanyMapping.objects.all().order_by('videoGame__release')
        games = []

        for mapping in gameMappings:
            if mapping.company.id == self.object.id and mapping.videoGame not in games:
                    games.append(mapping.videoGame)
        context['oldestGames'] = games[:50]
        if len(games) > 50:
            context['newestGames'] = games[-50:]

        context['books'] = BookCompanyMapping.objects.filter(company=self.object.id).order_by('book__release')
        context['webseries'] = WebSeriesCompanyMapping.objects.filter(company=self.object.id).order_by('webSeries__release')
        context['franchises'] = FranchiseCompanyMapping.objects.filter(company=self.object.id)
        context['gameFranchises'] = VideoGameFranchiseCompanyMapping.objects.filter(company=self.object.id)
        return context

class FranchiseDetailView(generic.DetailView):
    model = Franchise
    template_name = 'media/franchiseDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #Retrieve all subcategories for this franchise
        subcategories = FranchiseSubcategory.objects.filter(parentFranchise=self.object.id).order_by('subCategoryOrder')
        context['subcategories'] = subcategories

        if subcategories != None:
            for x in range(subcategories.count()):
                SubCat_F = FilmFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_TV = TelevisionFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_VG = VideoGameFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_B = BookFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_WS = WebSeriesFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)

                #Collect and sort all the media for that subcategory based on the 'orderInFranchise' field
                completeSubCategory = sorted(list(chain(SubCat_F, SubCat_TV, SubCat_VG, SubCat_B, SubCat_WS)), key=attrgetter('orderInFranchise'))
                #Dynamic context name for the subcategory in the template
                context[subcategories[x].title] = completeSubCategory

        franchiseFilms = FilmFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseTelevision = TelevisionFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseVideoGames = VideoGameFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseBooks = BookFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseWebSeries = WebSeriesFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)

        completeFranchise = list(chain(franchiseFilms, franchiseTelevision, franchiseVideoGames, franchiseBooks, franchiseWebSeries))

        franchiseActors = {}
        franchiseProducers = {}

        for media in completeFranchise:
            if hasattr(media,'film'):
                crew = FilmPersonMapping.objects.filter(film=media.film)
            if hasattr(media,'television'):
                crew = TelevisionPersonMapping.objects.filter(television=media.television)
            if hasattr(media,'videogame'):
                crew = VideoGamePersonMapping.objects.filter(videoGame=media.videoGame)
            if hasattr(media,'book'):
                crew = BookPersonMapping.objects.filter(book=media.book)
            if hasattr(media,'webseries'):
                crew = WebSeriesPersonMapping.objects.filter(webSeries=media.webSeries)

            cast = crew.filter(role=1)
            for mapping in cast:
                if mapping.person not in franchiseActors:
                    franchiseActors[mapping.person] = 1
                else:
                    franchiseActors[mapping.person] += 1

            producers = crew.filter(role=6)
            for mapping in producers:
                if mapping.person not in franchiseProducers:
                    franchiseProducers[mapping.person] = 1
                else:
                    franchiseProducers[mapping.person] += 1

        actorTuples = dict(sorted(franchiseActors.items(), key=operator.itemgetter(1), reverse=True))
        #sortedActors = {k: v for k,v in actorTuples}

        producerTuples = sorted(franchiseProducers.items(), key=operator.itemgetter(1), reverse=True)
        sortedProducers = {k: v for k,v in producerTuples}

        context['franchiseActors'] = actorTuples
        context['franchiseProducers'] = sortedProducers

        return context

class VideoGameFranchiseDetailView(generic.DetailView):
    model = VideoGameFranchise
    template_name = 'media/gameFranchiseDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #Determine how many subcategories there are
        subcategories = VideoGameFranchiseSubcategory.objects.filter(parentFranchise=self.object.id).order_by('subCategoryOrder')
        context['subcategories'] = subcategories

        if subcategories != None:
            for x in range(subcategories.count()):
                subCatGames = VideoGameVideoGameFranchiseSubcategoryMapping.objects.filter(
                    videoGameFranchiseSubcategory__parentFranchise=self.object.id).filter(videoGameFranchiseSubcategory__title=subcategories[x].title)

                #Collect all media for that subcategory
                completeSubCat = sorted(list(subCatGames), key=attrgetter('orderInFranchise'))

                #Dynamic context name for the subcategory in the template
                context[subcategories[x].title] = completeSubCat

        return context

class FilmDetailView(generic.UpdateView):
    model = Film
    template_name = 'media/filmDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    def post(self, request, *args, **kwargs):
        mediaPagePostRequests(self, request, *args, **kwargs)
        return super(FilmDetailView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = FilmGenreMapping.objects.filter(film=self.object.id)
        context['cast'] = FilmPersonMapping.objects.filter(role=1, film=self.object.id).order_by('billing')
        context['directors'] = FilmPersonMapping.objects.filter(role=2, film=self.object.id).order_by('billing')
        context['writers'] = FilmPersonMapping.objects.filter(role=3, film=self.object.id).order_by('billing')
        context['producers'] = FilmPersonMapping.objects.filter(role=6, film=self.object.id).order_by('billing')
        context['distributors'] = FilmCompanyMapping.objects.filter(role=1, film=self.object.id)
        context['productionCompanies'] = FilmCompanyMapping.objects.filter(role=2, film=self.object.id)
        context['images'] = FilmImages.objects.filter(film=self.object.id)
        context['nominationCount'] = FilmAwardMapping.objects.filter(film=self.object.id).count()
        context['winCount'] = FilmAwardMapping.objects.filter(film=self.object.id, win=True).count()
        context['tags'] = FilmTagMapping.objects.filter(film=self.object.id)

        franchises = []
        for x in FilmFranchiseSubcategoryMapping.objects.filter(film=self.object.id):
            if x.film.id == self.object.id:
                franchises.append(x.franchiseSubcategory.parentFranchise)
        context['franchises'] = franchises

        if self.object.budget:
            context['budgetFormatted'] = '$' + format(self.object.budget, ",")

        if self.object.boxOffice:
            context['boxOfficeFormatted'] = '$' + format(self.object.boxOffice, ",")

        ratings = FilmRating.objects.filter(film=self.object.id)
        ratingCount = ratings.count()
        context['ratingCount'] = ratingCount
        if ratingCount > 0:
            ratingSum = 0
            for rating in ratings:
                ratingSum += rating.rating
            average = ratingSum/ratingCount
            averageRating = "{:.1f}".format(average)
            context['averageRating'] = averageRating
            context['averageRatingText'] = "{:.1f}".format(float(averageRating)/2)

            if self.request.user.is_authenticated:
                r = FilmRating.objects.filter(user=self.request.user, film=self.object.id).first()
                if r is not None:
                    context['userRating'] = r.rating
                    context['userRatingText'] = r.rating / 2
                    if r.review is not None:
                        context['review'] = r.review

        if self.request.user.is_authenticated:
            context['inList'] = False
            for listFilm in UserListFilmMapping.objects.filter(user=self.request.user):
                if listFilm.film.id == self.object.id:
                    context['inList'] = True
                    break

        return context


class FilmCrewDetailView(FilmDetailView):
    template_name = 'media/filmCrewDetail.html'


class TVDetailView(generic.UpdateView):
    model = Television
    template_name = 'media/tvDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    def post(self, request, *args, **kwargs):
        mediaPagePostRequests(self, request, *args, **kwargs)
        return super(TVDetailView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = TelevisionGenreMapping.objects.filter(television=self.object.id).order_by('genre__title')
        context['cast'] = TelevisionPersonMapping.objects.filter(role=1, television=self.object.id).order_by('billing')
        context['showrunners'] = TelevisionPersonMapping.objects.filter(role=4, television=self.object.id)
        context['writers'] = TelevisionPersonMapping.objects.filter(role=3, television=self.object.id)
        context['producers'] = TelevisionPersonMapping.objects.filter(role=6, television=self.object.id).order_by('billing')
        context['networks'] = TelevisionCompanyMapping.objects.filter(role=3, television=self.object.id)
        context['productionCompanies'] = TelevisionCompanyMapping.objects.filter(role=2, television=self.object.id)
        context['images'] = TelevisionImages.objects.filter(television=self.object.id)

        franchises = []
        for x in TelevisionFranchiseSubcategoryMapping.objects.filter(television=self.object.id):
            if x.television.id == self.object.id:
                franchises.append(x.franchiseSubcategory.parentFranchise)
        context['franchises'] = franchises

        ratings = TelevisionRating.objects.filter(television=self.object.id)
        ratingCount = ratings.count()
        context['ratingCount'] = ratingCount
        if ratingCount > 0:
            ratingSum = 0
            for rating in ratings:
                ratingSum += rating.rating
            average = ratingSum/ratingCount
            averageRating = "{:.1f}".format(average)
            context['averageRating'] = averageRating
            context['averageRatingText'] = "{:.1f}".format(float(averageRating)/2)

            if self.request.user.is_authenticated:
                r = TelevisionRating.objects.filter(user=self.request.user, television=self.object.id).first()
                if r is not None:
                    context['userRating'] = r.rating
                    context['userRatingText'] = r.rating / 2
                    if r.review is not None:
                        context['review'] = r.review

        if self.request.user.is_authenticated:
            context['inList'] = False
            for listtv in UserListTelevisionMapping.objects.filter(user=self.request.user):
                if listtv.television.id == self.object.id:
                    context['inList'] = True
                    break

        return context


class TVCrewDetailView(TVDetailView):
    template_name = 'media/tvCrewDetail.html'


class VideoGameDetailView(generic.UpdateView):
    model = VideoGame
    template_name = 'media/gameDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    def post(self, request, *args, **kwargs):
        mediaPagePostRequests(self, request, *args, **kwargs)
        return super(VideoGameDetailView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = VideoGameGenreMapping.objects.filter(videoGame=self.object.id)
        context['consoles'] = VideoGameConsoleMapping.objects.filter(videoGame=self.object.id).order_by('console__name')
        context['developers'] = VideoGameCompanyMapping.objects.filter(role=4, videoGame=self.object.id)
        context['publishers'] = VideoGameCompanyMapping.objects.filter(role=5, videoGame=self.object.id)
        context['images'] = VideoGameImages.objects.filter(videoGame=self.object.id)
        context['actors'] = VideoGamePersonMapping.objects.filter(role=1, videogame=self.object.id)
        context['directors'] = VideoGamePersonMapping.objects.filter(role=2, videogame=self.object.id)
        context['writers'] = VideoGamePersonMapping.objects.filter(role=3, videogame=self.object.id)
        context['producers'] = VideoGamePersonMapping.objects.filter(role=6, videogame=self.object.id)
        context['cast'] = VideoGamePersonMapping.objects.filter(role=1, videogame=self.object.id).order_by('billing')

        franchises = []
        for x in VideoGameVideoGameFranchiseSubcategoryMapping.objects.filter(videoGame=self.object.id):
            if x.videoGame.id == self.object.id:
                franchises.append(x.videoGameFranchiseSubcategory.parentFranchise)
        context['franchises'] = franchises

        ratings = VideoGameRating.objects.filter(videoGame=self.object.id)
        ratingCount = ratings.count()
        context['ratingCount'] = ratingCount
        if ratingCount > 0:
            ratingSum = 0
            for rating in ratings:
                ratingSum += rating.rating
            average = ratingSum/ratingCount
            averageRating = "{:.1f}".format(average)
            context['averageRating'] = averageRating
            context['averageRatingText'] = "{:.1f}".format(float(averageRating)/2)

            if self.request.user.is_authenticated:
                r = VideoGameRating.objects.filter(user=self.request.user, videoGame=self.object.id).first()
                if r is not None:
                    context['userRating'] = r.rating
                    context['userRatingText'] = r.rating / 2
                    if r.review is not None:
                        context['review'] = r.review

        if self.request.user.is_authenticated:
            context['inList'] = False
            for listvg in UserListVideoGameMapping.objects.filter(user=self.request.user):
                if listvg.videoGame.id == self.object.id:
                    context['inList'] = True
                    break

        return context


class VideoGameCrewDetailView(VideoGameDetailView):
    template_name = 'media/gameCrewDetail.html'


class BookDetailView(generic.UpdateView):
    model = Book
    template_name = 'media/bookDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    def post(self, request, *args, **kwargs):
        mediaPagePostRequests(self, request, *args, **kwargs)
        return super(BookDetailView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = BookGenreMapping.objects.filter(book=self.object.id)
        context['authors'] = BookPersonMapping.objects.filter(role=3, book=self.object.id)
        context['publishers'] = BookCompanyMapping.objects.filter(role=5, book=self.object.id)

        franchises = []
        for x in BookFranchiseSubcategoryMapping.objects.filter(book=self.object.id):
            if x.book.id == self.object.id:
                franchises.append(x.franchiseSubcategory.parentFranchise)
        context['franchises'] = franchises

        ratings = BookRating.objects.filter(book=self.object.id)
        ratingCount = ratings.count()
        context['ratingCount'] = ratingCount
        if ratingCount > 0:
            ratingSum = 0
            for rating in ratings:
                ratingSum += rating.rating
            average = ratingSum/ratingCount
            averageRating = "{:.1f}".format(average)
            context['averageRating'] = averageRating
            context['averageRatingText'] = "{:.1f}".format(float(averageRating)/2)

            if self.request.user.is_authenticated:
                r = BookRating.objects.filter(user=self.request.user, book=self.object.id).first()
                if r is not None:
                    context['userRating'] = r.rating
                    context['userRatingText'] = r.rating / 2

        if self.request.user.is_authenticated:
            context['inList'] = False
            for listb in UserListBookMapping.objects.filter(user=self.request.user):
                if listb.book.id == self.object.id:
                    context['inList'] = True
                    break

        return context


class WebSeriesDetailView(generic.UpdateView):
    model = WebSeries
    template_name = 'media/webDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    def post(self, request, *args, **kwargs):
        mediaPagePostRequests(self, request, *args, **kwargs)
        return super(WebSeriesDetailView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = WebSeriesGenreMapping.objects.filter(webSeries=self.object.id).order_by('genre__title')
        context['cast'] = WebSeriesPersonMapping.objects.filter(role=1, webSeries=self.object.id).order_by('billing')
        context['showrunners'] = WebSeriesPersonMapping.objects.filter(role=4, webSeries=self.object.id)
        context['writers'] = WebSeriesPersonMapping.objects.filter(role=3, webSeries=self.object.id)
        context['producers'] = WebSeriesPersonMapping.objects.filter(role=6, webSeries=self.object.id)
        context['networks'] = WebSeriesCompanyMapping.objects.filter(role=3, webSeries=self.object.id)
        context['productionCompanies'] = WebSeriesCompanyMapping.objects.filter(role=2, webSeries=self.object.id)

        franchises = []
        for x in WebSeriesFranchiseSubcategoryMapping.objects.filter(webSeries=self.object.id):
            if x.webSeries.id == self.object.id:
                franchises.append(x.franchiseSubcategory.parentFranchise)
        context['franchises'] = franchises

        context['images'] = WebSeriesImages.objects.filter(webSeries=self.object.id)

        ratings = WebSeriesRating.objects.filter(webSeries=self.object.id)
        ratingCount = ratings.count()
        context['ratingCount'] = ratingCount
        if ratingCount > 0:
            ratingSum = 0
            for rating in ratings:
                ratingSum += rating.rating
            average = ratingSum/ratingCount
            averageRating = "{:.1f}".format(average)
            context['averageRating'] = averageRating
            context['averageRatingText'] = "{:.1f}".format(float(averageRating)/2)

            if self.request.user.is_authenticated:
                r = WebSeriesRating.objects.filter(user=self.request.user, webSeries=self.object.id).first()
                if r is not None:
                    context['userRating'] = r.rating
                    context['userRatingText'] = r.rating / 2
                    if r.review is not None:
                        context['review'] = r.review

        if self.request.user.is_authenticated:
            context['inList'] = False
            for listws in UserListWebSeriesMapping.objects.filter(user=self.request.user):
                if listws.webSeries.id == self.object.id:
                    context['inList'] = True
                    break

        return context


class GenreDetailView(generic.DetailView):
    model = Genre
    template_name = 'media/genreDetail.html'
    slug_field, slug_url_kwarg = "title", "title"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['franchises'] = FranchiseGenreMapping.objects.filter(genre=self.object.id)[:30]
        context['teensFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["2010-01-01", "2019-12-25"])[:30]
        context['naughtiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["2000-01-01", "2009-12-25"])[:30]
        context['ninetiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1990-01-01", "1999-12-25"])[:30]
        context['eightiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1980-01-01", "1989-12-25"])[:30]
        context['seventiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1970-01-01", "1979-12-25"])[:30]
        context['sixtiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1960-01-01", "1969-12-25"])[:30]
        context['fiftiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1950-01-01", "1959-12-25"])[:30]
        context['fortiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1940-01-01", "1949-12-25"])[:30]
        context['tv'] = TelevisionGenreMapping.objects.filter(genre=self.object.id).order_by('-television__release')[:30]
        context['games'] = VideoGameGenreMapping.objects.filter(genre=self.object.id).order_by('-videoGame__release')[:30]
        context['books'] = BookGenreMapping.objects.filter(genre=self.object.id).order_by('-book__release')[:30]
        context['webseries'] = WebSeriesGenreMapping.objects.filter(genre=self.object.id).order_by('-webSeries__release')[:30]
        return context


class TagDetailView(generic.DetailView):
    model = Tag
    template_name = 'media/tagDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['films'] = FilmTagMapping.objects.filter(tag=self.object.name)
        context['television'] = TelevisionTagMapping.objects.filter(tag=self.object.name)

        return context


class VideoGameGenreDetailView(generic.DetailView):
    model = VideoGameGenre
    template_name = 'media/gameGenreDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['franchises'] = VideoGameFranchiseGenreMapping.objects.filter(genre=self.object.id)
        context['projects'] = VideoGameGenreMapping.objects.filter(genre=self.object.id).order_by('videoGame__release')
        return context

class ConsoleDetailView(generic.DetailView):
    model = Console
    template_name = 'media/consoleDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        featured = []
        all = []
        for g in VideoGameConsoleMapping.objects.filter(console=self.object.id).order_by('videoGame__release'):
            if g.featured:
                featured.append(g)
            else:
                all.append(g)

        context['games'] = all[-100:]
        context['featuredGames'] = featured
        context['versions'] = ConsoleVersion.objects.filter(console=self.object.id).order_by('release')
        return context


# REST API Views Below #

from rest_framework import viewsets, permissions
from .serializers import *
from .serializers import *


class FilmSerializerView(viewsets.ModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer


class TelevisionSerializerView(viewsets.ModelViewSet):
    queryset = Television.objects.all()
    serializer_class = TelevisionSerializer



