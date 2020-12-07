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

def calculateRatings(quantity, reverse):
    films = Film.objects.all()
    filmRatingsDict = {}

    for f in films:
        fRatings = FilmRating.objects.filter(film=f)
        fRatingsCount = fRatings.count()
        if fRatingsCount > 0:
            fRatingSum = 0
            for rating in fRatings:
                fRatingSum += rating.rating
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
    context = {
        'films':Film.objects.all().order_by('-id')[:30],
        'newestFilms':Film.objects.all().order_by('release')[:30],
        'tv':Television.objects.all()[:30],
        'longestRunningTV':Television.objects.all().order_by('-episodes')[:30],
        'games':VideoGame.objects.all()[:30],
        'books':Book.objects.all()[:30],
        'webseries':WebSeries.objects.all()[:30],
        'people':Person.objects.all().order_by('DoB')[:30],
        'bornToday': Person.objects.all().filter(DoB__day=date.today().day).filter(DoB__month=date.today().month),
        'highestRatedFilms':calculateRatings(20, True),
        'topGrossing':calculateTopGrossing(30),
    }

    return render(request, 'media/home.html', context)

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
        'seventies':Film.objects.all().filter(release__range=["1970-01-01", "1979-12-25"]),
        'eighties': Film.objects.all().filter(release__range=["1980-01-01", "1989-12-25"]),
        'seventies':Film.objects.all().filter(release__range=["1970-01-01", "1979-12-25"]),
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
        'topRated':calculateRatings(100, True),
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
        context['television'] = TelevisionAwardCreditMapping.objects.filter(TelevisionAwardMapping__category=self.object.id).filter(TelevisionAwardMapping__win=True)
        context['videogames'] = VideoGameAwardCreditMapping.objects.filter(VideoGameAwardMapping__category=self.object.id).filter(VideoGameAwardMapping__win=True)
        context['books'] = BookAwardCreditMapping.objects.filter(BookAwardMapping__category=self.object.id).filter(BookAwardMapping__win=True)
        context['webseries'] = WebSeriesAwardCreditMapping.objects.filter(WebSeriesAwardMapping__category=self.object.id).filter(WebSeriesAwardMapping__win=True)
        return context

class PersonDetailView(generic.DetailView):
    model = Person
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

class FilmDetailView(generic.DetailView):
    model = Film
    template_name = 'media/filmDetail.html'
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
        context['images'] = FilmImages.objects.filter(film=self.object.id)
        context['nominationCount'] = FilmAwardMapping.objects.filter(film=self.object.id).count()
        context['winCount'] = FilmAwardMapping.objects.filter(film=self.object.id, win=True).count()
        context['tags'] = FilmTagMapping.objects.filter(film=self.object.id)

        franchises = []
        for x in FilmFranchiseSubcategoryMapping.objects.filter(film=self.object.id):
            if x.film.id == self.object.id:
                print("hello")
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

            if self.request.user.is_authenticated:
                r = FilmRating.objects.filter(user=self.request.user, film=self.object.id).first()
                if r is not None:
                    context['userRating'] = r.rating

        if self.request.user.is_authenticated:
            context['inList'] = False
            for listFilm in UserListFilmMapping.objects.filter(user=self.request.user):
                if listFilm.film.id == self.object.id:
                    context['inList'] = True
                    break

        listForm = FilmListForm()

        context['ratingForm'] = filmRatingForm()

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


class TVDetailView(generic.DetailView):
    model = Television
    template_name = 'media/tvDetail.html'
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
        context['images'] = TelevisionImages.objects.filter(television=self.object.id)

        franchises = []
        for x in TelevisionFranchiseSubcategoryMapping.objects.filter(television=self.object.id):
            if x.television.id == self.object.id:
                print("hello")
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

        return context

class VideoGameDetailView(generic.DetailView):
    model = VideoGame
    template_name = 'media/gameDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"

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

        return context

class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'media/bookDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"

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

        return context

class WebSeriesDetailView(generic.DetailView):
    model = WebSeries
    template_name = 'media/webDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"

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
        return context

class GenreDetailView(generic.DetailView):
    model = Genre
    template_name = 'media/genreDetail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['franchises'] = FranchiseGenreMapping.objects.filter(genre=self.object.id)
        context['naughtiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["2000-01-01", "2009-12-25"])
        context['ninetiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1990-01-01", "1999-12-25"])
        context['eightiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1980-01-01", "1989-12-25"])
        context['seventiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1970-01-01", "1979-12-25"])
        context['sixtiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1960-01-01", "1969-12-25"])
        context['fiftiesFilms'] = FilmGenreMapping.objects.filter(genre=self.object.id).filter(film__release__range=["1950-01-01", "1959-12-25"])
        context['tv'] = TelevisionGenreMapping.objects.filter(genre=self.object.id).order_by('television__release')
        context['games'] = VideoGameGenreMapping.objects.filter(genre=self.object.id).order_by('videoGame__release')
        context['books'] = BookGenreMapping.objects.filter(genre=self.object.id).order_by('book__release')
        context['webseries'] = WebSeriesGenreMapping.objects.filter(genre=self.object.id).order_by('webSeries__release')
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



