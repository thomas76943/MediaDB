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

from django.shortcuts import render, redirect
from django.views import generic
from django.db.models import Q
from .models import *
from users.models import *
from .forms import *
from django.db.models import Count

import requests, json, datetime, re
from django.core.files import File

def addUsers():
    with open("D:/MediaDB Datasets/movielensSmall/users.csv", 'r') as users:
        userData = csv.reader(users)

        for row in userData:
            print("Creating - ", row[1])
            user = User.objects.create_user(username=row[1], email=row[3], password=row[2])
            print("Created - ", row[1])

def addRatings():
    ratingsFile = open("D:/MediaDB Datasets/movielensSmall/ratingsCopy.csv", "rt")
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
            knownIDs[imdbID] = title #Adding to knownIDs

            #If not in database already, add new film
            if title not in filmTitles:
                filmTitles.append(title)
                print("Adding new film:", title)

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

def calculateHighestRated(quantity, reverse):
    films = Film.objects.all()
    filmRatingsDict = {}

    for f in films:
        fRatings = FilmRating.objects.filter(film=f)
        fRatingsCount = fRatings.count()
        if fRatingsCount > 30:
            fRatingSum = 0
            for rating in fRatings:
                fRatingSum += float(rating.rating / 2)
            fRatingAverage = (fRatingSum / fRatingsCount)
            average2DP = "{:.1f}".format(fRatingAverage)
            filmRatingsDict[f] = average2DP

    #Anonymous function takes x and returns float(x[1]) (ie: the score as a float), used in the key parameter to sort dict
    sortedRatings = dict(sorted(filmRatingsDict.items(), key=lambda x: float(x[1]), reverse=reverse))
    highestRated = dict(itertools.islice(sortedRatings.items(), quantity))
    return highestRated

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

def postRequest(self, request, *args, **kwargs):
    object = self.get_object()
    print(type(object))

    if self.request.user.is_authenticated:

        # POST Request: Adding/Removing from List
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
        else:
            newRating = float(request.POST['nr']) * 2
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
                    rating = WebSeries(user=self.request.user, webSeries=object, rating=newRating)
                rating.save()

    return super(FilmDetailView, self).post(request, *args, **kwargs)

def dataSources(request):
    fImages = FilmImages.objects.all()
    tvImages = TelevisionImages.objects.all()
    vgImages = VideoGameImages.objects.all()
    bImages = BookImages.objects.all()
    wsImages = WebSeriesImages.objects.all()
    images = sorted(list(chain(fImages, tvImages, vgImages, bImages, wsImages)), key=attrgetter("id"))
    context = {
        'images':images
    }
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

def home(request):

    oldest = []
    for p in Person.objects.all().order_by('DoB'):
        if p.DoB != None:
            oldest.append(p)
        if len(oldest) == 30:
            break

    context = {
        'films':Film.objects.all().order_by('-id')[:30],
        'newestFilms':Film.objects.all().order_by('release')[:30],
        'tv':Television.objects.all()[:30],
        'longestRunningTV':Television.objects.all().order_by('-episodes')[:30],
        'games':VideoGame.objects.all()[:30],
        'books':Book.objects.all()[:30],
        'webseries':WebSeries.objects.all()[:30],
        'people':oldest,
        'bornToday': Person.objects.all().filter(DoB__day=date.today().day).filter(DoB__month=date.today().month),
        'highestRatedFilms':calculateHighestRated(20, True),
        'topGrossing':calculateTopGrossing(30),
    }

    #addRatings()

    return render(request, 'media/home.html', context)

import collections

def testing(request):
    monthList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    months = {}
    for p in Person.objects.all().order_by('DoB__month'):
        if p.DoB != None:
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
        'counts':findDulplicateTitles(),
        'people':months
    }
    return render (request, 'media/testingPage.html', context)

def searchResults(request):
    title_contains = request.GET.get('q')

    context = {}

    if title_contains != '' and title_contains is not None:
        people = []
        for p in Person.objects.all():
            if p.getFullName().lower().__contains__(title_contains):
              people.append(p)

        context = {
            'searchQuery':title_contains,
            #'people':Person.objects.all().filter(Q(firstName__icontains=title_contains) | Q(surname__icontains=title_contains)).order_by('surname'),
            'people':people,
            'franchises': Franchise.objects.all().filter(title__icontains=title_contains).order_by('title'),
            'videogamefranchises': VideoGameFranchise.objects.all().filter(title__icontains=title_contains).order_by('title'),
            'consoles' : Console.objects.all().filter(Q(name__icontains=title_contains) | Q(shortName__icontains=title_contains)).order_by('name'),
            'films':Film.objects.all().filter(title__icontains=title_contains).order_by('title'),
            'tv':Television.objects.all().filter(title__icontains=title_contains).order_by('title'),
            'games':VideoGame.objects.all().filter(title__icontains=title_contains).order_by('title'),
            'books':Book.objects.all().filter(title__icontains=title_contains).order_by('title'),
            'webseries':WebSeries.objects.all().filter(title__icontains=title_contains).order_by('title'),
            'companies': Company.objects.all().filter(name__icontains=title_contains).order_by('name'),
        }
    return render(request, 'media/searchResults.html', context)

def browse(request):
    context = {
        'films': Film.objects.all(),
        'tv': Television.objects.all(),
        'videoGames': VideoGame.objects.all(),
        'books': Book.objects.all(),
        'webSeries': WebSeries.objects.all(),
        'people': Person.objects.all(),

    }

    if request.user.is_authenticated:
        userRatings = FilmRating.objects.filter(user=request.user)
        seenFilms = []
        for ur in userRatings:
            seenFilms.append(ur.film)
        context['seenFilms'] = seenFilms

    return render(request, 'media/browse.html', context)

def filmHome(request):
    context = {
        'films': Film.objects.all(),
        'franchises':Franchise.objects.all(),
        'genres':Genre.objects.all(),
        'seventies':Film.objects.all().filter(release__range=["1970-01-01", "1979-12-25"])[:30],
        'eighties': Film.objects.all().filter(release__range=["1980-01-01", "1989-12-25"])[:30],
        'nineties':Film.objects.all().filter(release__range=["1990-01-01", "1999-12-25"])[:30],
    }
    return render(request, 'media/filmHome.html', context)

def tvHome(request):
    context = {
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
            gameCompanies.append(vgcm.company)
    for vgcm in VideoGameCompanyMapping.objects.filter(role=5):
        if vgcm.company not in gameCompanies:
            gameCompanies.append(vgcm.company)

    context = {
        'games': VideoGame.objects.all(),
        'consoles': Console.objects.all().order_by('-release'),
        'franchises':VideoGameFranchise.objects.all()[:30],
        'genres': VideoGameGenre.objects.all(),
        'companies': gameCompanies,
    }
    return render(request, 'media/gameHome.html', context)

def bookHome(request):
    context = {
        'books':Book.objects.all(),
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

    filmForm = ContributeFilmForm(request.POST or None, initial={
        'title':'', 'release':'', 'rating':'', 'synopsis':'', 'length':'',
        'budget':'', 'boxOffice':'', 'posterFilePath':'', 'trailerVideoPath':''
    })

    televisionForm = ContributeTelevisionForm(request.POST or None, initial={
        'title':'', 'release':'', 'synopsis':'', 'seasons':'', 'episodes':'',
        'budget':'', 'boxOffice':'', 'posterFilePath':'', 'trailerVideoPath':''
    })

    forms = [filmForm, televisionForm]

    context = {
        'forms':forms,
    }

    if request.method == 'POST':
        if filmForm.is_valid():
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
    context = {
        'franchises': VideoGameFranchise.objects.all()
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
        'topRated':calculateHighestRated(100, True),
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
        context['films'] = FilmPersonMapping.objects.filter(person=self.object.id).order_by('film__release')
        context['tv'] = TelevisionPersonMapping.objects.filter(person=self.object.id).order_by('television__release')
        context['videogames'] = VideoGamePersonMapping.objects.filter(person=self.object.id).order_by('videogame__release')
        context['books'] = BookPersonMapping.objects.filter(person=self.object.id).order_by('book__release')
        context['webseries'] = WebSeriesPersonMapping.objects.filter(person=self.object.id).order_by('webSeries__release')
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
        context['games'] = games

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

        #Determine how many subcategories there are
        subcategories = FranchiseSubcategory.objects.filter(parentFranchise=self.object.id).order_by('subCategoryOrder')
        context['subcategories'] = subcategories

        if subcategories != None:
            for x in range(subcategories.count()):
                SubCat_F = FilmFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_TV = TelevisionFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_VG = VideoGameFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_B = BookFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_WS = WebSeriesFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)

                #Collect all media for that subcategory
                completeSubCat = sorted(list(chain(SubCat_F, SubCat_TV, SubCat_VG, SubCat_B, SubCat_WS)), key=attrgetter('orderInFranchise'))

                #Dynamic context name for the subcategory in the template
                context[subcategories[x].title] = completeSubCat

        franchiseFilms = FilmFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseTelevision = TelevisionFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseVideoGames = VideoGameFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseBooks = BookFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseWebSeries = WebSeriesFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)

        completeFranchise = list(chain(franchiseFilms, franchiseTelevision, franchiseVideoGames, franchiseBooks, franchiseWebSeries))

        franchisePeople = {}
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
                if mapping.person not in franchisePeople:
                    franchisePeople[mapping.person] = 1
                else:
                    franchisePeople[mapping.person] += 1

        tuples = sorted(franchisePeople.items(), key=operator.itemgetter(1), reverse=True)
        sortedPeople = {k: v for k,v in tuples}
        context['franchisePeople'] = sortedPeople

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
                subCatGames = VideoGameFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)

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
    """
    def post(self, request, *args, **kwargs):
        object = self.get_object()

        if self.request.user.is_authenticated:

            #List Toggle Request
            if request.POST['type'] == "listToggle":

                toggle = request.POST['toggle']
                if toggle == "add":
                    l = UserListFilmMapping(user=self.request.user, film=object)
                    l.save()
                else:
                    UserListFilmMapping.objects.filter(user=self.request.user, film=object.id).delete()

            #Rating Post Request
            else:

                newRating = float(request.POST['nr'])*2

                r = FilmRating.objects.filter(user=self.request.user, film=object.id).first()
                #If Updating a Rating
                if r is not None:
                    r.rating = newRating
                    r.save()
                #If Creating a New Rating
                else:
                    rating = FilmRating(user=self.request.user, film=object, rating=newRating)
                    rating.save()

                print("New Rating (DB):")
                r = FilmRating.objects.filter(user=self.request.user, film=object.id).first()
                print(r.rating)
    
        return super(FilmDetailView, self).post(request, *args, **kwargs)
    """

    def post(self, request, *args, **kwargs):
        postRequest(self,request,*args,**kwargs)
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

        if self.request.user.is_authenticated:
            context['inList'] = False
            for listFilm in UserListFilmMapping.objects.filter(user=self.request.user):
                if listFilm.film.id == self.object.id:
                    context['inList'] = True
                    break

        return context


class FilmCrewDetailView(generic.DetailView):
    model = Film
    template_name = 'media/filmCrewDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = FilmGenreMapping.objects.filter(film=self.object.id)
        context['cast'] = FilmPersonMapping.objects.filter(role=1, film=self.object.id).order_by('billing')
        context['directors'] = FilmPersonMapping.objects.filter(role=2, film=self.object.id).order_by('billing')
        context['writers'] = FilmPersonMapping.objects.filter(role=3, film=self.object.id).order_by('billing')
        context['producers'] = FilmPersonMapping.objects.filter(role=6, film=self.object.id).order_by('billing')
        context['distributors'] = FilmCompanyMapping.objects.filter(role=1, film=self.object.id)
        context['productionCompanies'] = FilmCompanyMapping.objects.filter(role=2, film=self.object.id)
        context['tags'] = FilmTagMapping.objects.filter(film=self.object.id)
        return context


class TVDetailView(generic.UpdateView):
    model = Television
    template_name = 'media/tvDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    def post(self, request, *args, **kwargs):
        postRequest(self,request,*args,**kwargs)
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
            context['averageRating'] = "{:.1f}".format(average)

            if self.request.user.is_authenticated:
                r = TelevisionRating.objects.filter(user=self.request.user, television=self.object.id).first()
                if r is not None:
                    context['userRating'] = r.rating
                    context['userRatingText'] = r.rating / 2

        if self.request.user.is_authenticated:
            context['inList'] = False
            for listtv in UserListTelevisionMapping.objects.filter(user=self.request.user):
                if listtv.television.id == self.object.id:
                    context['inList'] = True
                    break

        return context


class TVCrewDetailView(generic.DetailView):
    model = Television
    template_name = 'media/tvCrewDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = TelevisionGenreMapping.objects.filter(television=self.object.id).order_by('genre__title')
        context['cast'] = TelevisionPersonMapping.objects.filter(role=1, television=self.object.id).order_by('billing')
        context['showrunners'] = TelevisionPersonMapping.objects.filter(role=4, television=self.object.id)
        context['writers'] = TelevisionPersonMapping.objects.filter(role=3, television=self.object.id)
        context['producers'] = TelevisionPersonMapping.objects.filter(role=6, television=self.object.id).order_by('billing')
        context['networks'] = TelevisionCompanyMapping.objects.filter(role=3, television=self.object.id)
        context['productionCompanies'] = TelevisionCompanyMapping.objects.filter(role=2, television=self.object.id)
        return context


class VideoGameDetailView(generic.UpdateView):
    model = VideoGame
    template_name = 'media/gameDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    def post(self, request, *args, **kwargs):
        postRequest(self,request,*args,**kwargs)
        return super(VideoGameDetailView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = VideoGameGenreMapping.objects.filter(videoGame=self.object.id)
        context['consoles'] = VideoGameConsoleMapping.objects.filter(videoGame=self.object.id).order_by('console__name')
        context['developers'] = VideoGameCompanyMapping.objects.filter(role=4, videoGame=self.object.id)
        context['publishers'] = VideoGameCompanyMapping.objects.filter(role=5, videoGame=self.object.id)
        context['images'] = VideoGameImages.objects.filter(videoGame=self.object.id)

        franchises = []
        for x in VideoGameFranchiseSubcategoryMapping.objects.filter(videoGame=self.object.id):
            if x.videoGame.id == self.object.id:
                print("hello")
                franchises.append(x.franchiseSubcategory.parentFranchise)
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

        if self.request.user.is_authenticated:
            context['inList'] = False
            for listvg in UserListVideoGameMapping.objects.filter(user=self.request.user):
                if listvg.videoGame.id == self.object.id:
                    context['inList'] = True
                    break

        return context


class BookDetailView(generic.UpdateView):
    model = Book
    template_name = 'media/bookDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    def post(self, request, *args, **kwargs):
        postRequest(self,request,*args,**kwargs)
        return super(BookDetailView, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = BookGenreMapping.objects.filter(book=self.object.id)
        context['authors'] = BookPersonMapping.objects.filter(role=5, book=self.object.id)
        context['publishers'] = BookCompanyMapping.objects.filter(role=5, book=self.object.id)

        franchises = []
        for x in BookFranchiseSubcategoryMapping.objects.filter(book=self.object.id):
            if x.book.id == self.object.id:
                print("hello")
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
        postRequest(self,request,*args,**kwargs)
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
                print("hello")
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['franchises'] = FranchiseGenreMapping.objects.filter(genre=self.object.id)[:30]
        context['naughtiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["2000-01-01", "2009-12-25"])[:30]
        context['ninetiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1990-01-01", "1999-12-25"])[:30]
        context['eightiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1980-01-01", "1989-12-25"])[:30]
        context['seventiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1970-01-01", "1979-12-25"])[:30]
        context['sixtiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1960-01-01", "1969-12-25"])[:30]
        context['fiftiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1950-01-01", "1959-12-25"])[:30]
        context['fortiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1940-01-01", "1949-12-25"])[:30]
        context['tv'] = TelevisionGenreMapping.objects.filter(genre=self.object.id).order_by('television__release')[:30]
        context['games'] = VideoGameGenreMapping.objects.filter(genre=self.object.id).order_by('videoGame__release')[:30]
        context['books'] = BookGenreMapping.objects.filter(genre=self.object.id).order_by('book__release')[:30]
        context['webseries'] = WebSeriesGenreMapping.objects.filter(genre=self.object.id).order_by('webSeries__release')[:30]
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
        context['games'] = VideoGameConsoleMapping.objects.filter(console=self.object.id).order_by('videoGame__release')
        context['versions'] = ConsoleVersion.objects.filter(console=self.object.id).order_by('release')
        return context


# REST API Views Below #

from rest_framework import viewsets, permissions
from .serializers import *


class FilmSerializerView(viewsets.ModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer


class TelevisionSerializerView(viewsets.ModelViewSet):
    queryset = Television.objects.all()
    serializer_class = TelevisionSerializer



