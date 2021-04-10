import csv, io, itertools, operator, locale, requests, json, collections, re, time
from itertools import chain
from operator import attrgetter

from django import http
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.paginator import Paginator, EmptyPage
from django.db.models.functions import Length
from django.urls import reverse
from django.shortcuts import render, redirect
from django.views import generic
from django.db.models import Count, Q

from .models import *
from .forms import *
from .filters import *
from users.models import *
from users.views import *

import datetime
import numpy as np
import pandas as pd
from django_pandas.io import read_frame
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
from sklearn.metrics.pairwise import cosine_similarity
from datetime import date

#Finds and like-minded peers based on Film Ratings using Pearson Correlations and stores result in the database
#Parameters - userA: the active user
#Returns    - n/a
def calculateUserUserSimilarities(userA):
    #Create dictionary of all seen fimls
    seen = {}
    for ur in FilmRating.objects.filter(user=userA):
        seen[ur.film] = ur.rating

    #Create dictionary for user-user similarity scores
    similarities = {}
    for userB in User.objects.all():
        if userB != userA:
            userAScores = []
            userBScores = []
            #If users A (active user) and B (other) have seen a film, add rating scores to lists
            for fr in FilmRating.objects.filter(user=userB):
                if fr.film in seen:
                    userAScores.append(seen[fr.film])
                    userBScores.append(fr.rating)
            #If they have seen at least 5 of the same films, calculate Pearson Correlation between rating lists
            if len(userBScores) > 4:
                similarity = np.corrcoef((np.array(userAScores)).flatten(), (np.array(userBScores)).flatten())[0, 1]
                similarities[userB.id] = similarity
                print(similarities[userB.id])

    #Sort user-user similarities by the degree of correlation and retrieve the 20 most similar users
    sortedSimilarities = dict(sorted(similarities.items(), key=lambda x: float(x[1]), reverse=True)[:20])
    idStore = json.dumps(sortedSimilarities)

    uus = UserUserSimilarities.objects.filter(user=userA).first()
    #If user has not already stored its peers in the database, create a record
    if not uus:
        UserUserSimilarities(user=userA, users=idStore).save()
    #Otherwise, update the record where the users stores its peers
    else:
        uus.users = idStore
        uus.save()

#Retrieves a user's like-minded peers from the database
#Parameters - user: the active user
#Returns    - similarities: the 20 most similar users
def getUserUserSimilarities(user):
    users = []
    jsondecoder = json.decoder.JSONDecoder()
    uus = UserUserSimilarities.objects.filter(user=user).first()
    #If a record exists for this user's peers in the database, return the users
    if uus:
        similarities = jsondecoder.decode(uus.users)
        return similarities
    #Otherwise, calculate the user's peers and recursively call this function to retrieve them
    else:
        calculateUserUserSimilarities(user)
        getUserUserSimilarities(user)

#Retrieves the media seen/watched/played/read by the give user
#Parameters - user - the whose media is media is to be collected
#           - mediaType - the type of media to be collected (eg Films, Books etc)
#Returns    - seen - the set of media the user has seen/watched/played/read
def getSeen(user, mediaType):
    seen = []
    if mediaType == Film:
        #Iterate over each rating made for this media type
        for rating in FilmRating.objects.filter(user=user):
            #Store the media in a list if it is not already present
            if rating.film not in seen:
                seen.append(rating.film)
    if mediaType == Television:
        for rating in TelevisionRating.objects.filter(user=user):
            if rating.television not in seen:
                seen.append(rating.television)
    if mediaType == VideoGame:
        for rating in VideoGameRating.objects.filter(user=user):
            if rating.videoGame not in seen:
                seen.append(rating.videoGame)
    if mediaType == Book:
        for rating in BookRating.objects.filter(user=user):
            if rating.book not in seen:
                seen.append(rating.book)
    if mediaType == WebSeries:
        for rating in WebSeriesRating.objects.filter(user=user):
            if rating.webSeries not in seen:
                seen.append(rating.webSeries)
    return seen

#Performs collaborative filtering film recommendation for the given user
#Parameters - user: the active user
#Returns    - collaborativeResults: the set of recommended films
def collaborativeFiltering(user):
    #Visual choice to limit the float formatting to show only 1 dp
    pd.set_option('display.float_format', lambda x: '%.1f' % x)

    #Establish a dataframe and store the database's film records
    films = read_frame(Film.objects.all(), fieldnames=['id', 'title', 'slug'])

    #Establish a dataframe that concatenates various sections of the FilmRating database records
    #SQLite's MAX_VARIABLES limitation means this must be performed in several steps, cannot convert all ratings into a dataframe in one operation
    filmRatings = pd.concat([read_frame(FilmRating.objects.all()[:20000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[20001:40000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[40001:50000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[50001:60000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[60001:69000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[69001:75000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[75001:80000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[80001:86000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[86001:92000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[92001:98000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[98001:100000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[100001:102000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[102001:105000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[105001:107000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[107001:109000], fieldnames=['id', 'film', 'user', 'rating']),
                read_frame(FilmRating.objects.all()[109001:], fieldnames=['id', 'film', 'user', 'rating']),
    ])

    #Merge the films and ratings dataframes based on the Film's "title" field and the FilmRating's "film" field
    df = pd.merge(films, filmRatings, left_on='title', right_on='film')

    #Arrange fields for the combined dataframe and create a column for the total ratings count
    combine_film_rating = df.dropna(axis=0, subset=['id_x'])
    combine_film_rating = df.dropna(axis=0, subset=['title'])
    film_ratingCount = (combine_film_rating.
        groupby(by=['title'])['rating'].
        count().
        reset_index().
        rename(columns={'rating': 'totalRatingCount'})
        [['title', 'totalRatingCount']])

    #Merge dataframes with grouping, resetted indexes and the new totalRatingcount column
    rating_with_totalRatingCount = combine_film_rating.merge(film_ratingCount, left_on='title', right_on='title', how='left')

    #Querying result to filter out films with fewer than 25 ratings
    popularity_threshold = 5
    rating_popular_movie = rating_with_totalRatingCount.query('totalRatingCount >= @popularity_threshold')

    #Create a pivot table with zeros to indicate no Film-User mapping (indicates no rating)
    movie_features_df = rating_popular_movie.pivot_table(index=['id_x','slug'], columns='user', values='rating').fillna(0)

    # Converting pivot table into "Compressed Sparse Row" (CSR) Matrix (efficient arithmetic and row slicing (films), slow column slicing (users))
    movie_features_df_matrix = csr_matrix(movie_features_df.values)

    #Apply nearest neighbours using cosine similarity and the 'brute force' approach and fit the dataset
    model_knn = NearestNeighbors(metric='cosine', algorithm='brute')
    model_knn.fit(movie_features_df_matrix)

    #Retrieve the active user's peers
    peers = getUserUserSimilarities(user)

    collaborativeResults = []
    #For each of the 50 films rated highest by the peers
    for hr in FilmRating.objects.filter(user__in=peers).order_by('-rating')[:50]:
        query_index = hr.film.id
        #Check to ensure the film exists in the CSR matrix
        if not movie_features_df[movie_features_df.index.get_level_values('id_x') == query_index].empty:
            #Find the nearest neighbours to that fiml
            distances, indices = model_knn.kneighbors(movie_features_df[movie_features_df.index.get_level_values('id_x') == query_index].values.reshape(1, -1), n_neighbors=25)
            for i in range(1, len(distances.flatten())):
                    #Retrieve the film's unique slug through its index in the CSR matrix
                    slug = movie_features_df.index[indices.flatten()[i]][1]
                    #If the film is not already being recommended, add it to the recommendations result
                    if slug not in collaborativeResults:
                        collaborativeResults.append(Film.objects.get(slug=slug))

    return collaborativeResults

#Retrieves a particular user's feed based on the profiles they follow
#Parameters - user: the user whose feed is to be found
#           - limit: the number of items in the feed to retrieve
#Returns    - feed: the combined set of media items making up the feed
#           - following: the profiles that the user follows
def getFeed(user, limit):
    following = UserFollows.objects.filter(userA=user)
    f = []
    #For each account the user follows, retrieve their media ratings and chain the result into one list
    for account in following:
        accountFilms = FilmRating.objects.filter(user=account.userB)
        accountTV = TelevisionRating.objects.filter(user=account.userB)
        accountVG = VideoGameRating.objects.filter(user=account.userB)
        accountBooks = BookRating.objects.filter(user=account.userB)
        accountWeb = WebSeriesRating.objects.filter(user=account.userB)
        accountRatings = list(chain(accountFilms, accountTV, accountVG, accountBooks, accountWeb))
        for ar in accountRatings:
            f.append(ar)
    #Sort all of the activity feed items based on their 'datetime' fields, with the most recent first
    feed = sorted(f, key=attrgetter('dateTime'), reverse=True)[:limit]
    return feed, following

#Retrieves a generic activity feed to be used when the active user does not follow any other users
#Parameters - limit: the number of items in the feed to retrieve
#Returns    - feed: the combined set of media items making up this generic activity feed
def getAllActivity(limit):
    f = []
    #Iterate over each user profile and retrieve their media ratings
    for account in User.objects.all():
        accountFilms = FilmRating.objects.filter(user=account)
        accountTV = TelevisionRating.objects.filter(user=account)
        accountVG = VideoGameRating.objects.filter(user=account)
        accountBooks = BookRating.objects.filter(user=account)
        accountWeb = WebSeriesRating.objects.filter(user=account)
        accountRatings = list(chain(accountFilms, accountTV, accountVG, accountBooks, accountWeb))
        for ar in accountRatings:
            f.append(ar)
    #Sort all users' media ratings by the most recent dates and times
    return sorted(f, key=attrgetter('dateTime'), reverse=True)[:limit]

#Temporary
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

    badCharsTitles = ['?', '/', '#', '!', '"', '<', '>', '[', ']', '{', '}', '@', 'Ã', 'Â', '©', '¢', '€', 'ž', '¦', ]
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

#Recalculates the highest-rated items of a particular media type
#Parameters - mediaType - the database table corresponding to the type of media for which the highest-rated items should be found (eg Films, Books etc)
#           - highestRatingType - the database table where the results should be stored
#           - minRatings - the minimum number of ratings required for the media item to be considered
#           - quantity - the number of highest-rated items that should be found
#           - reverse - whether the function should give the highest or lowest average ratings first
#Returns    - n/a
def recalculateHighestRated(mediaType, highestRatingType, minRatings, quantity, reverse):

    #Remove the database's current stores of the highest rated media
    top = highestRatingType.objects.all()
    for t in top:
        t.delete()

    media = mediaType.objects.all()
    ratingsDict = {}
    #Iterate through each item of that media type and retrieve its ratings
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
        #Count the number of ratings
        ratingsCount = ratings.count()
        #If there are more than the minimum required to be counted
        if ratingsCount >= minRatings:
            ratingSum = 0
            for rating in ratings:
                ratingSum += float(rating.rating / 2)
            #Calculate the average and store in the ratingsDict dictionary
            ratingAverage = (ratingSum / ratingsCount)
            average2DP = "{:.1f}".format(ratingAverage)
            ratingsDict[m] = average2DP

    #Sort the ratings dictionary.
    #Anonymous lambda function takes x and returns float(x[1]) (ie: the average rating as a float) and sorts based on this value
    sortedRatings = dict(sorted(ratingsDict.items(), key=lambda x: float(x[1]), reverse=reverse))

    #Retrieve as many of the highest rated items as defined in the 'quantity' parameter
    highestRated = dict(itertools.islice(sortedRatings.items(), quantity))

    #Store the highest rated items as new records in the database
    count=1
    for hr in highestRated:
        highestRatingType(media=hr, rating=highestRated[hr], rank=count).save()
        count += 1

#Retrieves the highest-rated items of a particular media type
#Parameters - mediaType - the database table corresponding to the type of media for which the highest-rated items should be retrieved (eg Films, Books etc)
#           - quantity - the number of highest-rated items that should be retrieved
#Returns    - the highest rated items of a particular media type
def getHighestRated(mediaType, quantity):
    if mediaType == Film:
        return HighestRatedFilms.objects.all().order_by('rank')[:quantity]
    if mediaType == Television:
        return HighestRatedTelevision.objects.all().order_by('rank')[:quantity]
    if mediaType == VideoGame:
        return HighestRatedVideoGames.objects.all().order_by('rank')[:quantity]
    if mediaType == Book:
        return HighestRatedBooks.objects.all().order_by('rank')[:quantity]
    return HighestRatedWebSeries.objects.all().order_by('rank')[:quantity]

#Retrieves the highest-grossing films from the database
#Parameters - quantity - the number of highest-rated items that should be retrieved
#Returns    - the highest rated items of a particular media type
def getTopGrossing(quantity):
    topGrossing = Film.objects.all().order_by('-boxOffice')[:quantity]
    filmGrossingDict = {}

    #For each of the top grossing films queried
    for f in topGrossing:
        #Format the film's box office field value
        gross = float('{:.3g}'.format(f.boxOffice))
        magnitude = 0
        #Establish incremental symbols
        symbols = ['', 'K', 'M', 'B', 'T']
        while abs(gross) >= 1000:
            magnitude += 1
            gross /= 1000.0
        #Format the box office value by stripping and applying the correct number of magnitude values
        filmGrossingDict[f] = '$' + '{}{}'.format('{:.3f}'.format(gross).rstrip('0'), symbols[magnitude])

    return filmGrossingDict

#The POST request handler function for media detail pages. Handles lists, ratings and reviews
#Parameters     - self - refers to 'self' of the media page UpdateView from which this function was called
#               - request - the request object from which the current user object is retrieved
#               - *args - the arguments taken from the media page UpdateView's post() method
#               - *kwargs - the keyword arguments taken from the media page UpdateView's post() method
def mediaPagePostRequests(self, request, *args, **kwargs):
    #Retrieve the object (Film, TV, Book etc) itself
    object = self.get_object()
    if self.request.user.is_authenticated:
        #If the POST request type is "listToggle", the POST Request is for: Adding/Removing the item from the user's List
        if request.POST['type'] == "listToggle":
            #Retrieve the toggle state, either "Add" or "Remove"
            toggle = request.POST['toggle']
            #Adding Media to List
            if toggle == "add":
                #Creating a mapping between the user and the Film/TV/Game/Book/WebSeries as required
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
                #Save the new record
                l.save()
            else:
                #Removing a mapping between the user and the Film/TV/Game/Book/WebSeries as required
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

        #If the POST request type is "rating", the POST Request is for: Adding/Updating the user's rating for this item
        elif request.POST['type'] == "rating":

            #Attempt to retrieve the new rating value
            newRating = float(request.POST['nr'])
            #Retrieve the necessary database object that maps the user to the media item
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

            #If the database record already exists, the function will be updating a rating
            if r is not None:
                #Save the new score and the date+time when the rating was made
                r.rating = newRating
                r.dateTime = datetime.datetime.now()
                r.save()
            #Otherwise, if the database record does not exist, the fucntion will be creating a new rating
            else:
                #Create a new record in the appropriate database rating table
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
                #Save the new rating record
                rating.save()

        #In the third case, the POST request is for: Creating/Updating the user's review of this item
        else:
            #Retrieve the 'newReview' from the POST request
            newReview = request.POST['newReview']
            if newReview:
                #Retrieve the necessary database record for the user's rating of the media item
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

                #Update the 'review' field of the rating object to contain the new/updated review
                r.review = newReview
                #Store the time at which the review was created/updated
                r.dateTime = datetime.datetime.now()
                r.save()

    return super(FilmDetailView, self).post(request, *args, **kwargs)

#Retrieves the upcoming media items that have not been released yet.
#Can work for any one media type or any combination of media types
#Parameters     - f - boolean to represent whether the upcoming films should be returned
#               - tv - boolean to represent whether the upcoming television series should be returned
#               - vg - boolean to represent whether the upcoming video games should be returned
#               - b - boolean to represent whether the upcoming books should be returned
#               - ws - boolean to represent whether the upcoming web series should be returned
#Returns        - allUpcoming - the combination set of upcoming media items
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

    allUpcoming = sorted(upcoming, key=attrgetter('release'))
    return allUpcoming

#Retrieves the highest rated films a particular user has not seen
#Parameters     - user - the for which the unseen films should be found
#Returns        - unseen - the unseen films
def topRatedUnseen(user):
    userFilmRatings = FilmRating.objects.filter(user=user)
    topRated = getHighestRated(Film, 500)
    seen = []
    unseen = []
    #Iterate through the user's film ratings
    for rating in userFilmRatings:
        seen.append(rating.film)
    #Iterate through the top rated films
    for tr in topRated:
        #If the user has not seen the film, add the film to a list
        if tr.media not in seen:
            unseen.append(tr.media)
    #Return a maximum of 500 top rated unseen films
    return unseen[:500]

#Finds the average score per genre given by a user to films in a particular input set. Used in content-based filtering
#Parameters     - user - the user whose average genre scores are to be found
#               - inputSet - the films from which the average genre scores should be found
#Returns        - genreAverages - a dictionary containing all of the genres and their average scores for this particular user
def genreScores(user, inputSet):
    userFilmRatings = FilmRating.objects.filter(user=user, film__in=inputSet)
    genreScores = {}
    genreAverages = {}
    #Iterate through each rating made the user
    for ufr in userFilmRatings:
        film = ufr.film
        rating = ufr.rating
        #Retrieve the film's genres
        genres = FilmGenreMapping.objects.filter(film=film)

        if genres:
            #For each genre
            for g in genres:
                genre = g.genre.title
                #Add the film's rating to a list of genre scores. Create this list if it does not already exist
                if genre not in genreScores:
                    genreScores[genre] = []
                    genreScores[genre].append(rating)
                else:
                    genreScores[genre].append(rating)

            #For each genre score list
            for gs in genreScores:
                sum = 0
                #Iterate through the genre scores
                for score in genreScores[gs]:
                    sum += score

                average = sum/len(genreScores[gs])
                genreAverages[gs] = average

    return genreAverages

#Creates a set of recommendations based on a particular user's average scores for each genre
#Parameters     - user - the user whose average genre scores are used to generate recommendations
#               - inputSet - the films from which the average genre scores should be used to generate recommendations
#Returns        - recommendations - a sorted dictionary containing all of the films and their predicted rating scores based on their genres
#               - genresScores - a dictionary containing each genre and its average score based on this particular user's ratings
def genreRecommender(user, inputSet):
    genresScores = genreScores(user, inputSet)
    trUnseen = topRatedUnseen(user)
    filmScores = {}

    #Iterate though top rated unseen films
    for unseen in trUnseen:
        score = 0
        #Retrieve the genres for the unseen films
        filmGenres = FilmGenreMapping.objects.filter(film=unseen)
        for genre in filmGenres:
            #For each genre, add the genreScore to a total score counter
            if genre.genre.title in genresScores:
                score += genresScores[genre.genre.title]
        #Divide by how many were used to find an average genre score
        if filmGenres.count() > 1:
            score = score / filmGenres.count()
        #Divide by 2 for front-end formatting purposes
        score = score/2
        #Store the film's genre score in a dictionary
        filmScores[unseen] = "{:.1f}".format(score)

    #Sort films by highest genre score
    recommendations = dict(sorted(filmScores.items(), key=lambda item: item[1], reverse=True)[:100])

    return recommendations, genresScores

#Finds the average score per person type given by a user to films in a particular input set. Used in content-based filtering
#Parameters     - user - the user whose average person scores are to be found
#               - personType - type of the person whose averages are to be found (Actors, Directors, Writers)
#               - inputSet - the films from which the average person scores should be found
#Returns        - peopleAveragesDict - a dictionary containing all of the people of this type and their average scores for this particular user
def peopleScores(user, personType, inputSet):
    #personTypes: 1 = Actor, 2 = Director, 3 = Writer, 4 = Showrunner, 5 = Author, 6 = Producer, 7 = Designer
    userFilmRatings = FilmRating.objects.filter(user=user, film__in=inputSet)
    peopleScoresDict = {}
    peopleAveragesDict = {}

    #Iterate over the user's ratings of the films in the inputSet
    for ufr in userFilmRatings:
        film = ufr.film
        rating = ufr.rating
        allCrew = FilmPersonMapping.objects.filter(film=film)
        people = allCrew.filter(role=personType)
        #If the film has people attached to it
        if people:
            for p in people:
                person = p.person
                #Apply the user's rating of the film to each of the users attached to the film
                if person not in peopleScoresDict:
                    peopleScoresDict[person] = []
                    peopleScoresDict[person].append(rating)
                else:
                    peopleScoresDict[person].append(rating)

    #For each person's set of scores
    for personScore in peopleScoresDict:
        if len(peopleScoresDict[personScore]) > 1:
            sum = 0
            for score in peopleScoresDict[personScore]:
                sum += score
            #Find their average score
            average = sum/len(peopleScoresDict[personScore])
            #Store the person and their score in a peopleAverages dictionary
            peopleAveragesDict[personScore] = float("{:.2f}".format(average))

    return peopleAveragesDict

#Creates a set of recommendations based on a particular user's average scores for each person type
#Parameters     - user - the user whose average person scores are to be used to generate recommendations
#               - personType - type of the person whose averages are to be used to generate recommendations
#               - inputSet - the films from which the average person scores should be used to generate recommendations
#               - recommendations - a sorted dictionary containing the recommended films and the predicted rating scores
#               - personSort - a sorted dictionary containing each person and their average score based on this particular user's ratings
#Returns        - recommendations - a sorted dictionary containing all of the films and their predicted rating scores based on the people's scores
#               - personSort - a sorted dictionary containing each person and their average score based on this particular user's ratings
def personRecommender(user, personType, inputSet):
    personScores = peopleScores(user, personType, inputSet)
    trUnseen = topRatedUnseen(user)
    filmScores = {}

    #Iterate over the top rated films unseen by the user
    for unseen in trUnseen:
        score = 0
        allFilmPeople = FilmPersonMapping.objects.filter(film=unseen)
        filmPeople = allFilmPeople.filter(role=personType)
        #For each of the people of this particular type attached to the film
        for person in filmPeople:
            if person.person in personScores:
                #Add their average rating to a total score counter
                score += personScores[person.person]
        #Divide by how many people were involved to obtain an averaeg
        if filmPeople.count() > 1:
            score = score / filmPeople.count()
        #Divide by 2 for front-end formatting purposes
        score = score / 2
        #Store the film and its associated predicted score in a filmScores dictionary
        filmScores[unseen] = "{:.1f}".format(score)

    # Sort the films by highest person score and retrieve the top 100
    recommendations = dict(sorted(filmScores.items(), key=lambda item: item[1], reverse=True)[:100])

    #Sort people by highest average scores
    personSort = dict(sorted(personScores.items(), key=lambda item: item[1], reverse=True))

    return recommendations, personSort

#Performs content-based filtering by combining the genreRecommender and personRecommender results
#Parameters     - user - the user for whom content-based filtering should be performed to recommend films based on their ratings
#               - inputSet - the films from which the function can generate recommendations using content-based filtering
#Returns        - contentBasedResults - an ordered set of film recommendations generated using content-based filtinerg
def contentBasedFiltering(user, inputSet):
    print("Input Set:", inputSet)
    #Run genreRecommender to generate genre-based recommendations
    genreRecommendations, genreScores = genreRecommender(user, inputSet)

    #Run personRecommender three times (for actors, directors and writers, respectively)
    directorRecommendations, directorScores = personRecommender(user, 2, inputSet)
    actorRecommendations, actorScores = personRecommender(user, 1, inputSet)
    writerRecommendations, writerScores = personRecommender(user, 3, inputSet)
    combinedrecommendations = {}

    #Combine the results of the genre-based, actor-based, director-based and writer-based recommenders
    for film in genreRecommendations:
        combinedrecommendations[film] = float(genreRecommendations[film])
    for film in directorRecommendations:
        if film not in combinedrecommendations:
            combinedrecommendations[film] = float(directorRecommendations[film])
        else:
            combinedrecommendations[film] += float(directorRecommendations[film])
    for film in actorRecommendations:
        if film not in combinedrecommendations:
            combinedrecommendations[film] = float(actorRecommendations[film])
        else:
            combinedrecommendations[film] += float(actorRecommendations[film])
    for film in writerRecommendations:
        if film not in combinedrecommendations:
            combinedrecommendations[film] = float(writerRecommendations[film])
        else:
            combinedrecommendations[film] += float(writerRecommendations[film])

    #Sort the combined items based on their predicted rating scores and return the result
    contentBasedResults = []
    ordered = sorted(combinedrecommendations.items(), key=lambda x: x[1], reverse=True)
    for key in ordered:
        contentBasedResults.append(key[0])
    print("ContentBasedResults:", contentBasedResults)
    return contentBasedResults

#Save the results of the recommender system for a particular user
#Parameters     - user - the user whose film recommendations are to be stored
#               - dataset - the set of films whose IDs are to be stored in the database
#Returns        - n/a
def saveRecommendations(user, dataset):
    #Iterate through the film dataset and retrieve their IDs
    combinedIDs = []
    for film in dataset:
        combinedIDs.append(film.id)
    #Convert the film IDs into JSON
    idStore = json.dumps(combinedIDs[:100])

    #Get the database object that stores the IDs of the users film recommendations
    fr = FilmRecommendations.objects.filter(user=user).first()

    #Create the object and store the IDs if the record does not exist
    if not fr:
        FilmRecommendations(user=user, films=idStore).save()
    #Or update the IDs of the films in the record
    else:
        fr.films = idStore
        fr.save()

#Retrieves the recommendations made for a particular user from the database
#Parameters     - user - the user whose film recommendations are to be retrieved
#Returns        - films - the set of recommended films
def getRecommendations(user):
    jsondecoder = json.decoder.JSONDecoder()

    films=[]
    #Retrieve the database record containing the IDs of the recommendded films (in JSON)
    recommendations = FilmRecommendations.objects.filter(user=user).first()
    if recommendations:
        #Decode the JSON. For each film, retrieve the film object corresponding to the ID, store the film in a list
        for id in jsondecoder.decode(recommendations.films):
            films.append(Film.objects.get(pk=id))
    #return the list of films
    return films

#Function-based view to render the recommendations page.
#The @login_required decorator means the user is asked to log in if they are not authenticated.
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the recommendations.html file with the contents of the context dictionary
@login_required
def recommendations(request):
    context = {}
    if request.user.is_authenticated:

        #Retrieve this user's recommendations from the database and store the films they have seen
        getResults = getRecommendations(request.user)
        context['seenFilms'] = getSeen(request.user, Film)

        #If accessing the page for the first time or clicking the "Generate" Button,
        #generate CF, CBF and Hybrid recommendations
        if request.method == "POST":
            #Step 1: Recalculate the most similar users
            calculateUserUserSimilarities(request.user)
            #Step 2: Perform collaborative filtering
            cf = collaborativeFiltering(request.user)
            hybrid = contentBasedFiltering(request.user, cf)
            saveRecommendations(request.user, hybrid)
            context['results'] = getRecommendations(request.user)

        #If it is a regular GET request, pass the recommender results to the context
        else:
            context['results'] = getResults

    return render(request, 'media/recommendations.html', context)

#Function-based view to render the detailed recommendations page
#The @login_required decorator means the user is asked to log in if they are not authenticated.
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the recommendationsDetail.html file with the contents of the context dictionary
@login_required
def recommendationsDetail(request):
    context = {}
    if request.user.is_authenticated:
        #Pass the user's seen films to the context
        context['seenFilms'] = getSeen(request.user, Film)

        #Pass the result of collaborative and content-based filtering separately to the context
        context['collaborativeFiltering'] = collaborativeFiltering(request.user)
        context['contentBasedFiltering'] = contentBasedFiltering(request.user, Film.objects.all())

        #Pass the results of the genre, director, actor and writer-based recommenders to the context
        genreRecommendations, genreScores = genreRecommender(request.user, Film.objects.all())
        context['genreRecommendations'] = genreRecommendations
        directorRecommendations, directorScores = personRecommender(request.user, 2, Film.objects.all())
        context['directorRecommendations'] = directorRecommendations
        actorRecommendations, actorScores = personRecommender(request.user, 1, Film.objects.all())
        context['actorRecommendations'] = actorRecommendations
        writerRecommendations, writerScores = personRecommender(request.user, 3, Film.objects.all())
        context['writerRecommendations'] = writerRecommendations

    return render(request, 'media/recommendationsDetail.html', context)

#Function-based view to render the MediaDB website's home page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the home.html file with the contents of the context dictionary
def home(request):

    #Information to be displayed on the website's home page is gathered in the context dictionary
    context = {
        'upcoming':getUpcomingTitles(f=True, tv=True, vg=True, b=True, ws=True),
        'longestRunningTV':Television.objects.all().order_by('-episodes')[:16],
        'books':Book.objects.all()[:30],
        'webseries':WebSeries.objects.all()[:30],
        'bornToday': Person.objects.all().filter(DoB__day=date.today().day).filter(DoB__month=date.today().month),
        'highestRatedFilms':getHighestRated(Film, 30),
        'topGrossing':getTopGrossing(16),
    }

    #If the user is logged in, additional context is supplied to the front-end
    #This includes the films they have seen and their followed users' activity
    if request.user.is_authenticated:
        seen = getSeen(request.user, Film)
        context['seenFilms'] = seen
        if len(seen) < 5:
            context['ratingMessage'] = "Rate at least 5 films to generate recommendations"
        else:
            getr = getRecommendations(request.user)
            if getr:
                context['recommendations'] = getr
            else:
                context['generateMessage'] = "Generate recommendations here"

        feed, following = getFeed(request.user, 16)
        if following.count() < 1:
            context['feed'] = getAllActivity(16)
        else:
            context['feed'] = feed
            context['personal'] = True

    #If the user is not logged in, a generic user activity feed is supplied to the context
    else:
        context['feed'] = getAllActivity(16)

    return render(request, 'media/home.html', context)

#Function-based view to render the calendar page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the calendar.html file with the contents of the context dictionary
def calendar(request):
    monthList = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    months = {}

    #Iterate over each person in the database
    for p in Person.objects.all().order_by('DoB__month'):
        #If the person's date of birth field is populated
        if p.DoB != None:
            #Retrieve the corresponding month string
            date = str(monthList[p.DoB.month - 1])
            #Add them to the list of people for this month
            if date in months:
                months[date].append(p)
            else:
                months[date] = []
                months[date].append(p)

    #Iterate over each month in the dictionary
    for month in months:
        #Sort the people born in that month by the day they were born
        monthSort = sorted(months[month], key=attrgetter('DoB.day'))
        #Overwrite the months key in the dictionary with this sorted list of names
        months[month] = monthSort

    #Supply the months dictionary (storing the people and their birth dates) to the context
    context = {
        'people':months
    }

    return render (request, 'media/calendar.html', context)

#Function-based view to render the data sources page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the dataSources.html file with the contents of the context dictionary
def dataSources(request):
    return render(request, "media/dataSources.html", {})

#Temporary
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
                videoGames.append(vg.title)

            title = game['name']

            if any(badChar in title for badChar in badCharsTitles):
                print("--- Skipped Game:", title, ". Invalid Characters")
                continue

            if 'first_release_date' not in game:
                print("--- Skipped Game:", title, ". Requires Release Date" )
                continue
            else:
                dateConv = time.strftime('%Y-%m-%d', time.localtime(game['first_release_date']))

            #slug = slugify(title + "-" + str(dateConv))

            if title in videoGames:
                print("--- Skipped Game:", title, ". Duplicate Title ---")
            else:
                print("--- Adding Game:", title)
                newGame = VideoGame()
                newGame.title = title
                newGame.release = dateConv
                newGame.save()

            #Getting Game (whether it is newly made or not)
            getGame = VideoGame.objects.filter(title=title)[0]

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

#Temporary
def addBookData():
    badCharsTitles = ['?', '/', '#', '!', '"', '<', '>', '[', ']', '{', '}', '@', 'Ã', 'Â', '©', '¢', '€', 'ž', '¦', ]

    with open("D:\MediaDB Datasets\gamesData.json", "r", encoding="utf8") as f:
        data = json.loads(f.read())

#Function-based view to render the search results page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the searchResults.html file with the contents of the context dictionary
def searchResults(request):

    #Retrieve the context of the query string from the request object
    title_contains = request.GET.get('q').lower()

    context = {}

    #If the title is not empty or none, gather the database objects that match/contain the query
    if title_contains != '' and title_contains is not None:

        peoplePictures = []
        peopleOther = []
        #Iterate over each person in the database
        for p in Person.objects.all():
            #If the person's name contains the string
            if p.getFullName().lower().__contains__(title_contains):
                #Add the person to differnt lists depending on whether they have an image associated with them
                if p.image == None or p.image == "MissingIcon.png":
                    peopleOther.append(p)
                else:
                    peoplePictures.append(p)

        companyPictures = []
        companyOther = []
        #Iterate over each company in the database
        for c in Company.objects.all():
            #If the company's name contains the string
            if c.name.lower().__contains__(title_contains):
                #Add the company to differnt lists depending on whether it has an image associated with it
                if c.image:
                    companyPictures.append(c)
                else:
                    companyOther.append(c)

        #Gather the remaining context items by filtering the database model records to contain the query string
        #Depending on the type of object, a maximum of 20, 25 or 72 objects of each type are displayed
        #This limit is implemented to fit various front-end containers on the front-end and not overwhelm the user with too many results
        context = {
            'searchQuery':title_contains,
            'peoplePictures':peoplePictures[:72],
            'peopleOther':peopleOther[:20],
            'franchises': Franchise.objects.all().filter(title__icontains=title_contains).order_by('id')[:25],
            'videogamefranchises': VideoGameFranchise.objects.all().filter(title__icontains=title_contains).order_by('id')[:25],
            'consoles' : Console.objects.all().filter(Q(name__icontains=title_contains) | Q(shortName__icontains=title_contains)).order_by('name')[:25],
            'films':Film.objects.all().filter(title__icontains=title_contains).order_by('id')[:72],
            'television':Television.objects.all().filter(title__icontains=title_contains).order_by('id')[:72],
            'games':VideoGame.objects.all().filter(title__icontains=title_contains).order_by('id')[:72],
            'books':Book.objects.all().filter(title__icontains=title_contains).order_by('id')[:72],
            'webseries':WebSeries.objects.all().filter(title__icontains=title_contains).order_by('id')[:72],
            'companiesPictures': companyPictures[:25],
            'companiesOthers': companyOther[:20],
        }

    return render(request, 'media/searchResults.html', context)

#Function-based view to render the media browsing grid page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the browse.html file with the contents of the context dictionary
#----NEED TO WORK ON THIS----#
def browse(request):

    films = Film.objects.all()
    television = Television.objects.all()
    videoGames = VideoGame.objects.all()
    books = Book.objects.all()
    webSeries = WebSeries.objects.all()
    people = Person.objects.exclude(image='MissingIcon.png')
    #print(people.count())
    """
    allMedia = list(chain(films, television, videoGames, books, webSeries, people))

    filteredFilms = filmFilter(request.GET, queryset=films)
    paginatedFilteredFilms = Paginator(filteredFilms.qs, 90)
    page_number = request.GET.get('page', 1)
    mediaPageObject = paginatedFilteredFilms.get_page(page_number)
    context = {
        'filteredFilms' : filteredFilms,
        'mediaPageObject': mediaPageObject,
        'seenFilms' : FilmRating.objects.filter(user=request.user)
    }

    """
    allMedia = list(chain(films, television, videoGames, books, webSeries, people))

    #filteredMedia = mediaFilter(request.GET, queryset=allMedia)
    paginatedMedia = Paginator(allMedia, 90)
    page_number = request.GET.get('page', 1)
    mediaPageObject = paginatedMedia.get_page(page_number)

    context = {
        'filteredFilms' : paginatedMedia,
        'mediaPageObject': mediaPageObject,
    }

    if request.user.is_authenticated:
        context['seenFilms'] = getSeen(request.user, Film)

    return render(request, 'media/browse.html', context)

#Function-based view to render the film home page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the filmHome.html file with the contents of the context dictionary
def filmHome(request):

    genres = []
    #For each genre
    g = Genre.objects.all()
    for genre in g:
        #If the genre has an image attached to it, add it to a list to display on the front-end
        if genre.image:
            genres.append(genre)

    #Provides the rest of the context for the film home page: the highest rated films,
    #franchises, genres and a breakdown of films by decade
    context = {
        'highestRatedFilms': getHighestRated(Film, 100),
        'franchises':Franchise.objects.all(),
        'genres':genres,
        'seventies':Film.objects.all().filter(release__range=["1970-01-01", "1979-12-25"])[:30],
        'eighties': Film.objects.all().filter(release__range=["1980-01-01", "1989-12-25"])[:30],
        'nineties':Film.objects.all().filter(release__range=["1990-01-01", "1999-12-25"])[:30],
    }

    return render(request, 'media/filmHome.html', context)

#Function-based view to render the television home page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the tvHome.html file with the contents of the context dictionary
def tvHome(request):

    genres = []
    #For each genre
    g = Genre.objects.all()
    for genre in g:
        #If the genre has an image attached to it, add it to a list to display on the front-end
        if genre.image:
            genres.append(genre)

    #Provides the rest of the context for the television home page:
    #the highest rated television series, genres and a breakdown of shows by decade
    context = {
        'highestRatedShows':getHighestRated(Television, 100),
        'shows': Television.objects.all(),
        'genres': genres,
        'nineties': Television.objects.all().filter(release__range=["1990-01-01", "1999-12-25"]),
        'naughties': Television.objects.all().filter(release__range=["2000-01-01", "2009-12-25"]),
        'tens': Television.objects.all().filter(release__range=["2010-01-01", "2019-12-25"]),
    }
    return render(request, 'media/tvHome.html', context)

#Function-based view to render the video game home page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the gameHome.html file with the contents of the context dictionary
def gameHome(request):

    gameCompanies = []

    #Iterate through videogame-company mappings, filtered where the role type = 4 (game developers)
    for vgcm in VideoGameCompanyMapping.objects.filter(role=4)[:50]:
        if vgcm.company not in gameCompanies:
            #If the company is not in the tracking list and has an image, store the record in the list
            if vgcm.company.image:
                gameCompanies.append(vgcm.company)

    #Iterate through videogame-company mappings, filtered where the role type = 5 (game publishers)
    for vgcm in VideoGameCompanyMapping.objects.filter(role=5)[:50]:
        if vgcm.company not in gameCompanies:
            #If the company is not in the tracking list and has an image, store the record in the list
            if vgcm.company.image:
                gameCompanies.append(vgcm.company)


    genres = []
    g = VideoGameGenre.objects.all()
    #For each video game genre
    for genre in g:
        #If the genre has an image attached to it, add it to a list to display on the front-end
        if genre.image:
            genres.append(genre)

    franchises = []
    #For each videogame-videogamefranchise mapping
    for vgf in VideoGameVideoGameFranchiseSubcategoryMapping.objects.all():
        #If the parent franchise of the mapping is not already in the trackling list, add it
        if vgf.videoGameFranchiseSubcategory.parentFranchise not in franchises:
            franchises.append(vgf.videoGameFranchiseSubcategory.parentFranchise)

    #Pass the required database querysets to the context dictionary: the highest rated
    #games, upcoming games, games consoles, game franchises and game companies
    context = {
        'topRated':getHighestRated(VideoGame, 20),
        'upcoming':getUpcomingTitles(f=False, tv=False, vg=True, b=False, ws=False),
        'consoles': Console.objects.all().order_by('-release'),
        'franchises':franchises[:50],
        'genres': genres,
        'companies': gameCompanies,
    }

    return render(request, 'media/gameHome.html', context)

#Function-based view to render the book home page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the bookHome.html file with the contents of the context dictionary
def bookHome(request):

    context = {
        'books':Book.objects.all(),
    }
    return render(request, 'media/bookHome.html', context)

#Function-based view to render the web series home page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the webHome.html file with the contents of the context dictionary
def webHome(request):
    context = {
        'webSeries': WebSeries.objects.all(),
    }
    return render(request, 'media/webHome.html', context)

#Function-based view to render the video game consoles home page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the consoleHome.html file with the contents of the context dictionary
def consoleHome(request):

    consolesFeaturedGames = {}
    sorted = {}
    #For each videogame-console mapping
    for map in VideoGameConsoleMapping.objects.all():
        #If the video game is a featured game for that console
        if map.featured:
            #Create lists and store the features games for each console in a dictionary
            if map.console not in consolesFeaturedGames:
                consolesFeaturedGames[map.console] = []
                consolesFeaturedGames[map.console].append(map.videoGame)
            else:
                consolesFeaturedGames[map.console].append(map.videoGame)

    #Pass the consoleFeaturedGames dictionary to the context dictionary
    context = {
        'consolesFeaturedGames':consolesFeaturedGames,
    }

    return render(request, "media/consoleHome.html", context)

#Function-based view to render the franchise home page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the franchiseHome.html file with the contents of the context dictionary
def franchiseHome(request):

    franchises = []
    #For each film franchise subcategory mapping
    for f in FilmFranchiseSubcategoryMapping.objects.all():
        #If the subcategory's parent franchise is not already in the tracking list, add it
        if f.franchiseSubcategory.parentFranchise not in franchises:
            franchises.append(f.franchiseSubcategory.parentFranchise)

    context = {
        'franchises':franchises
    }
    return render(request, 'media/franchisesHome.html', context)

#Function-based view to render the video game franchise home page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the gamefranchiseHome.html file with the contents of the context dictionary
def videoGameFranchiseHome(request):

    franchises = []
    #For each videogame-videogamefranchise subcategory mapping
    for vgf in VideoGameVideoGameFranchiseSubcategoryMapping.objects.all():
        #If the subcategory's parent franchise is not already in the tracking list, addit
        if vgf.videoGameFranchiseSubcategory.parentFranchise not in franchises:
            franchises.append(vgf.videoGameFranchiseSubcategory.parentFranchise)

    context = {
        'franchises':franchises,
    }
    return render(request, 'media/gameFranchiseHome.html', context)

#Function-based view to render the top grossing films page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the topGrossing.html file with the contents of the context dictionary
def topGrossing(request):

    topGrossing = {}
    #Retrieve the top 100 highest grossing films
    for film in Film.objects.all().order_by('-boxOffice')[:100]:
        #Format each film's box office for the front-end
        topGrossing[film] = '$' + format(film.boxOffice, ",")

    context = {
        'topGrossing':topGrossing,
    }
    return render(request, 'media/topGrossing.html', context)

#Function-based view to render the top rated films page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the topRated.html file with the contents of the context dictionary
def topRated(request):
    context = {
        'topRated':getHighestRated(Film, 100),
    }
    return render(request, 'media/topRated.html', context)

#Function-based view to render the awards home page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the awardsHome.html file with the contents of the context dictionary
def awardsHome(request):
    #Query the database for the different award types and the most recent awards shows
    context = {
        'shows':AwardsShow.objects.all().order_by('-date'),
        'types':AwardType.objects.all()
    }
    return render(request, 'media/awardsHome.html', context)

#Function-based view to render the contribution home page
#Parameters     - request - the request object containing the GET/POST data and user object
#Returns        - renders the contributHome.html file with the contents of the context dictionary
def contributeHome(request):
    return render(request, 'media/contributeHome.html')

#Class-based CreateView that handles, gathers the context for and renders a page with a contribution form.
#The first CreateView, 'contributeBase', serves as a parent from which all other contribution views inherit
#Each subsequent contribution CreateView overwrites the model attribute, corresponding to different database tables
class contributeBase(generic.CreateView):
    model = Film
    fields = '__all__'
    template_name = 'media/contributeBase.html'

    #Method to handle a successful
    def get_success_url(self):
        return reverse('contribute-home')

    #Method to detect and handle a valid contribution form submission
    def form_valid(self, form):
        post = form.save(commit=False)
        post.save()
        messages.success(self.request, f'Contribution Successful')
        return http.HttpResponseRedirect(reverse('contribute-home'))
class contributeTelevision(contributeBase):
    model = Television
class contributeVideoGame(contributeBase):
    model = VideoGame
class contributeBook(contributeBase):
    model = Book
class contributeWebSeries(contributeBase):
    model = WebSeries
class contributePerson(contributeBase):
    model = Person
class contributeCompany(contributeBase):
    model = Company
class contributeFilmPerson(contributeBase):
    model = FilmPersonMapping
    fields = None
    form_class = BaseMappingForm
class contributeFilmGenre(contributeBase):
    model = FilmGenreMapping
    fields = None
    form_class = FilmGenreMappingForm
class contributeFilmCompany(contributeBase):
    model = FilmCompanyMapping
    fields = None
    form_class = FilmCompanyMappingForm
class contributeFilmTag(contributeBase):
    model = FilmTagMapping
    fields = None
    form_class = FilmTagMappingForm
class contributeTelevisionPerson(contributeBase):
    model = TelevisionPersonMapping
    fields = None
    form_class = TelevisionPersonMappingForm
class contributeTelevisionGenre(contributeBase):
    model = TelevisionGenreMapping
    fields = None
    form_class = TelevisionGenreMappingForm
class contributeTelevisionCompany(contributeBase):
    model = TelevisionCompanyMapping
    fields = None
    form_class = TelevisionCompanyMappingForm
class contributeTelevisionTag(contributeBase):
    model = TelevisionTagMapping
    fields = None
    form_class = TelevisionTagMappingForm
class contributeVideoGamePerson(contributeBase):
    model = VideoGamePersonMapping
    fields = None
    form_class = VideoGamePersonMappingForm
class contributeVideoGameGenre(contributeBase):
    model = VideoGameGenreMapping
    fields = None
    form_class = VideoGameGenreMappingForm
class contributeVideoGameCompany(contributeBase):
    model = VideoGameCompanyMapping
    fields = None
    form_class = VideoGameCompanyMappingForm
class contributeVideoGameTag(contributeBase):
    model = VideoGameTagMapping
    fields = None
    form_class = VideoGameTagMappingForm
class contributeVideoGameConsole(contributeBase):
    model = VideoGameConsoleMapping
    fields = None
    form_class = VideoGameConsoleMappingForm
class contributeBookPerson(contributeBase):
    model = BookPersonMapping
    fields = None
    form_class = BookPersonMappingForm
class contributeBookGenre(contributeBase):
    model = BookGenreMapping
    fields = None
    form_class = BookGenreMappingForm
class contributeBookCompany(contributeBase):
    model = BookCompanyMapping
    fields = None
    form_class = BookCompanyMappingForm
class contributeBookTag(contributeBase):
    model = BookTagMapping
    fields = None
    form_class = BookTagMappingForm
class contributeWebSeriesPerson(contributeBase):
    model = WebSeriesPersonMapping
    fields = None
    form_class = WebSeriesPersonMappingForm
class contributeWebSeriesGenre(contributeBase):
    model = WebSeriesGenreMapping
    fields = None
    form_class = WebSeriesGenreMappingForm
class contributeWebSeriesCompany(contributeBase):
    model = WebSeriesCompanyMapping
    fields = None
    form_class = WebSeriesCompanyMappingForm
class contributeWebSeriesTag(contributeBase):
    model = WebSeriesTagMapping
    fields = None
    form_class = WebSeriesTagMappingForm

#Class-based DetailView that handles, gathers the context for and renders a page for a particular awards show
class AwardsShowDetail(generic.DetailView):
    model = AwardsShow
    template_name = 'media/awardShowDetail.html'

    #Method to set up the context data to pass to the template
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

#Class-based DetailView that handles, gathers the context for and renders a page for a particular award type
class AwardsTypeDetail(generic.DetailView):
    model = AwardType
    template_name = 'media/awardTypeDetail.html'

    # Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Retrieve the award shows sorted by the most recent
        context['shows'] = AwardsShow.objects.filter(award=self.object.id).order_by('-date')
        return context

#Class-based DetailView that handles, gathers the context for and renders a page for a particular award category
class AwardsCategoryDetail(generic.DetailView):
    model = AwardsCategories
    template_name = 'media/awardCategoryDetail.html'

    # Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #Retrieve each of the media items that have won an award in this category
        context['films'] = FilmAwardCreditMapping.objects.filter(FilmAwardMapping__category=self.object.id).filter(FilmAwardMapping__win=True)
        context['television'] = TelevisionAwardCreditMapping.objects.filter(TelevisionAwardMapping__category=self.object.id).filter(TelevisionAwardMapping__win=True)
        context['videogames'] = VideoGameAwardCreditMapping.objects.filter(VideoGameAwardMapping__category=self.object.id).filter(VideoGameAwardMapping__win=True)
        context['books'] = BookAwardCreditMapping.objects.filter(BookAwardMapping__category=self.object.id).filter(BookAwardMapping__win=True)
        context['webseries'] = WebSeriesAwardCreditMapping.objects.filter(WebSeriesAwardMapping__category=self.object.id).filter(WebSeriesAwardMapping__win=True)
        return context

#Class-based DetailView that handles, gathers the context for and renders a page for a particular person
class PersonDetailView(generic.DetailView):
    model = Person
    slug_field, slug_url_kwarg = "slug", "slug"
    template_name = 'media/personDetail.html'

    # Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #All mappings where this person was attached with role=1 (Actor) are retrieved
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
        #All the person are combined
        actingAll = list(chain(fActing, tvActing, vgActing, wsActing))
        #All the mappings are sorted by the most recent first
        acting = sorted(actingAll, key=attrgetter('release'), reverse=True)

        #All mappings where this person was attached with role=2 (Director) are retrieved
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
        #All the mappings are combined
        directingAll = list(chain(fDirecting, tvDirecting, vgDirecting, wsDirecting))
        # All the mappings are sorted by the most recent first
        directing = sorted(directingAll, key=attrgetter('release'), reverse=True)
#
        #All mappings where this person was attached with role=3 (Writer) are retrieved
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
        #All the mappings are combined
        writingAll = list(chain(fWriting, tvWriting, vgWriting, bWriting, wsWriting))
        # All the mappings are sorted by the most recent first
        writing = sorted(writingAll, key=attrgetter('release'), reverse=True)

        #All mappings where this person was attached with role=6 (Producer) are retrieved
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
        #All the mappings are combined
        producingAll = list(chain(fProducing, tvProducing, vgProducing, wsProducing))
        # All the mappings are sorted by the most recent first
        producing = sorted(producingAll, key=attrgetter('release'), reverse=True)

        #If the combined, sorted lists of mappings have entries, add them to a roleOrder dictionary
        roleOrder = {}
        if len(actingAll) > 0:
            roleOrder['Actor'] = acting
        if len(directingAll) > 0:
            roleOrder['Director'] = directing
        if len(writingAll) > 0:
            roleOrder['Writer'] = writing
        if len(producingAll) > 0:
            roleOrder['Producer'] = producing

        #Sort the roleOrder dictionary based on the number of items
        #(ie: the person's categories will be sorted by how many mappings there are of each type)
        ordered = sorted(roleOrder.items(), key= lambda x: len(x[1]), reverse=True)
        context['roles'] = ordered

        #Gather additional context information: additional images, award nominations and award wins
        context['images'] = PersonImages.objects.filter(person=self.object.id)
        context['nominationCount'] = FilmAwardCreditMapping.objects.filter(Person=self.object.id).count()
        context['winCount'] = FilmAwardCreditMapping.objects.filter(Person=self.object.id, FilmAwardMapping__win=True).count()
        return context

#Class-based DetailView that handles, gathers the context for and renders a page for a particular company
class CompanyDetailView(generic.DetailView):
    model = Company
    template_name = 'media/companyDetail.html'

    # Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #The oldest video games mapped to this company are found and passed to the context
        games=[]
        for id in VideoGameCompanyMapping.objects.filter(company_id=self.object.id).order_by('videoGame__release').values_list('videoGame', flat=True).distinct():
            games.append(VideoGame.objects.filter(pk=id).first())
        context['oldestGames'] = games[:100]

        #The newest video games mapped to this company are found and passed to the context
        games=[]
        for id in VideoGameCompanyMapping.objects.filter(company_id=self.object.id).order_by('-videoGame__release').values_list('videoGame', flat=True).distinct():
            games.append(VideoGame.objects.filter(pk=id).first())
        context['newestGames'] = games[:100]

        #Gather context information for a company's consoles, films television, books, web series and franchises
        context['consoles'] = Console.objects.filter(developer=self.object.id).order_by('-release')
        context['films'] = FilmCompanyMapping.objects.filter(company=self.object.id).order_by('film__release')
        context['television'] = TelevisionCompanyMapping.objects.filter(company=self.object.id).order_by('television__release')
        context['books'] = BookCompanyMapping.objects.filter(company=self.object.id).order_by('book__release')
        context['webseries'] = WebSeriesCompanyMapping.objects.filter(company=self.object.id).order_by('webSeries__release')
        context['franchises'] = FranchiseCompanyMapping.objects.filter(company=self.object.id)
        context['gameFranchises'] = VideoGameFranchiseCompanyMapping.objects.filter(company=self.object.id)
        return context

#Class-based DetailView that handles, gathers the context for and renders a page for a particular franchise
class FranchiseDetailView(generic.DetailView):
    model = Franchise
    template_name = 'media/franchiseDetail.html'

    # Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #Retrieve all subcategories for this franchise
        subcategories = FranchiseSubcategory.objects.filter(parentFranchise=self.object.id).order_by('subCategoryOrder')
        context['subcategories'] = subcategories

        if subcategories != None:
            #Iterate through each subcategory
            for x in range(subcategories.count()):
                #Retrieve the media items mapped to this subcategory
                SubCat_F = FilmFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_TV = TelevisionFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_VG = VideoGameFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_B = BookFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)
                SubCat_WS = WebSeriesFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id).filter(franchiseSubcategory__title=subcategories[x].title)

                #Collect and sort all the media for that subcategory based on the 'orderInFranchise' field
                completeSubCategory = sorted(list(chain(SubCat_F, SubCat_TV, SubCat_VG, SubCat_B, SubCat_WS)), key=attrgetter('orderInFranchise'))
                #Dynamic context name for the subcategory in the template
                context[subcategories[x].title] = completeSubCategory

        #All media mappings for this franchise, regardless of which are subcategory the items are in, are found
        franchiseFilms = FilmFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseTelevision = TelevisionFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseVideoGames = VideoGameFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseBooks = BookFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)
        franchiseWebSeries = WebSeriesFranchiseSubcategoryMapping.objects.filter(franchiseSubcategory__parentFranchise=self.object.id)

        #Every item in all subcategories are combined together
        completeFranchise = list(chain(franchiseFilms, franchiseTelevision, franchiseVideoGames, franchiseBooks, franchiseWebSeries))


        franchiseActors = {}
        franchiseProducers = {}
        #For each media item in the entire franchise
        for media in completeFranchise:
            crew = None
            #Retrieve all people mapped to this item
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

            if crew != None:
                #Filter the people mappings to just the actors
                cast = crew.filter(role=1)
                for mapping in cast:
                    #For each cast member, add them to a dictionary and keep a counter of how many media items they have acted in
                    if mapping.person not in franchiseActors:
                        franchiseActors[mapping.person] = 1
                    else:
                        franchiseActors[mapping.person] += 1

                #Filter the people mappings to just the producers
                producers = crew.filter(role=6)
                for mapping in producers:
                    #For each producer, add them to a dictionary and keep a counter of how many media items they have produced
                    if mapping.person not in franchiseProducers:
                        franchiseProducers[mapping.person] = 1
                    else:
                        franchiseProducers[mapping.person] += 1

        #Sorting the actor and producer dictionaries by how many mappings there are per person before passing this to the context
        context['franchiseActors'] = dict(sorted(franchiseActors.items(), key=operator.itemgetter(1), reverse=True))
        context['franchiseProducers'] = dict(sorted(franchiseProducers.items(), key=operator.itemgetter(1), reverse=True))

        return context

#Class-based DetailView that handles, gathers the context for and renders a page for a particular video game franchise
class VideoGameFranchiseDetailView(generic.DetailView):
    model = VideoGameFranchise
    template_name = 'media/gameFranchiseDetail.html'

    # Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #Determine how many subcategories there are
        subcategories = VideoGameFranchiseSubcategory.objects.filter(parentFranchise=self.object.id).order_by('subCategoryOrder')
        context['subcategories'] = subcategories

        if subcategories != None:
            #Iterate through each subcategory
            for x in range(subcategories.count()):
                #Retrieve the media items mapped to this subcategory
                subCatGames = VideoGameVideoGameFranchiseSubcategoryMapping.objects.filter(videoGameFranchiseSubcategory__parentFranchise=self.object.id).filter(videoGameFranchiseSubcategory__title=subcategories[x].title)

                #Collect and sort all the media for that subcategory based on the 'orderInFranchise' field
                completeSubCat = sorted(list(subCatGames), key=attrgetter('orderInFranchise'))

                #Dynamic context name for the subcategory in the template
                context[subcategories[x].title] = completeSubCat

        return context

#Class-based UpdateView that handles, gathers the context for and renders a page for a particular film
class FilmDetailView(generic.UpdateView):
    model = Film
    template_name = 'media/filmDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    #POST method to make a call to the mediaPagePostRequests handler
    def post(self, request, *args, **kwargs):
        mediaPagePostRequests(self, request, *args, **kwargs)
        return super(FilmDetailView, self).post(request, *args, **kwargs)

    # Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Collect the context for this film item
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

        #Retrieve the parent franchise based on the film-franchisesubcategory mapping
        franchises = []
        for x in FilmFranchiseSubcategoryMapping.objects.filter(film=self.object.id):
            if x.film.id == self.object.id:
                franchises.append(x.franchiseSubcategory.parentFranchise)
        context['franchises'] = franchises

        #Format the film's budget value for the front end
        if self.object.budget:
            context['budgetFormatted'] = '$' + format(self.object.budget, ",")

        #Format the film's box office value for the front end
        if self.object.boxOffice:
            context['boxOfficeFormatted'] = '$' + format(self.object.boxOffice, ",")

        #Retrieve the ratings of this film
        ratings = FilmRating.objects.filter(film=self.object.id)
        ratingCount = ratings.count()
        #Pass the number of ratings to the template
        context['ratingCount'] = ratingCount
        if ratingCount > 0:
            #Calculate the film's average rating
            ratingSum = 0
            for rating in ratings:
                ratingSum += rating.rating
            average = ratingSum/ratingCount
            #Format the average rating for the front end
            averageRating = "{:.1f}".format(average)
            context['averageRating'] = averageRating
            context['averageRatingText'] = "{:.1f}".format(float(averageRating)/2)

            #If the user is logged in, attempt to retrieve their rating of the film
            if self.request.user.is_authenticated:
                r = FilmRating.objects.filter(user=self.request.user, film=self.object.id).first()
                if r is not None:
                    #Pass the score and the
                    context['userRating'] = r.rating
                    context['userRatingText'] = r.rating / 2
                    if r.review is not None:
                        context['review'] = r.review

        #If the user is logged in, retrieve whether the film is in their list
        if self.request.user.is_authenticated:
            context['inList'] = False
            for listFilm in UserListFilmMapping.objects.filter(user=self.request.user):
                if listFilm.film.id == self.object.id:
                    context['inList'] = True
                    break

        return context

#Class-based DetailView that handles, gathers the context for and renders a page for a particular film crew (inherits from FilmDetail)
class FilmCrewDetailView(FilmDetailView):
    template_name = 'media/filmCrewDetail.html'

#Class-based UpdateView that handles, gathers the context for and renders a page for a particular television series
class TVDetailView(generic.UpdateView):
    model = Television
    template_name = 'media/tvDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    #POST method to make a call to the mediaPagePostRequests handler
    def post(self, request, *args, **kwargs):
        mediaPagePostRequests(self, request, *args, **kwargs)
        return super(TVDetailView, self).post(request, *args, **kwargs)

    # Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Collect the context for this film item
        context['genres'] = TelevisionGenreMapping.objects.filter(television=self.object.id).order_by('genre__title')
        context['cast'] = TelevisionPersonMapping.objects.filter(role=1, television=self.object.id).order_by('billing')
        context['showrunners'] = TelevisionPersonMapping.objects.filter(role=4, television=self.object.id)
        context['writers'] = TelevisionPersonMapping.objects.filter(role=3, television=self.object.id)
        context['producers'] = TelevisionPersonMapping.objects.filter(role=6, television=self.object.id).order_by('billing')
        context['networks'] = TelevisionCompanyMapping.objects.filter(role=3, television=self.object.id)
        context['productionCompanies'] = TelevisionCompanyMapping.objects.filter(role=2, television=self.object.id)
        context['images'] = TelevisionImages.objects.filter(television=self.object.id)

        #Retrieve the parent franchise based on the tv-franchisesubcategory mapping
        franchises = []
        for x in TelevisionFranchiseSubcategoryMapping.objects.filter(television=self.object.id):
            if x.television.id == self.object.id:
                franchises.append(x.franchiseSubcategory.parentFranchise)
        context['franchises'] = franchises

        #Retrieve the rating
        ratings = TelevisionRating.objects.filter(television=self.object.id)
        ratingCount = ratings.count()
        context['ratingCount'] = ratingCount
        if ratingCount > 0:
            ratingSum = 0
            for rating in ratings:
                ratingSum += rating.rating
            #Calculate the average rating
            average = ratingSum/ratingCount
            #Format the average rating for the front-end
            averageRating = "{:.1f}".format(average)
            context['averageRating'] = averageRating
            context['averageRatingText'] = "{:.1f}".format(float(averageRating)/2)

            #Attempt to retrieve the user's rating of this television series
            if self.request.user.is_authenticated:
                r = TelevisionRating.objects.filter(user=self.request.user, television=self.object.id).first()
                if r is not None:
                    context['userRating'] = r.rating
                    context['userRatingText'] = r.rating / 2
                    if r.review is not None:
                        context['review'] = r.review

        #If the user is logged in, retrieve whether the series is in their list
        if self.request.user.is_authenticated:
            context['inList'] = False
            for listtv in UserListTelevisionMapping.objects.filter(user=self.request.user):
                if listtv.television.id == self.object.id:
                    context['inList'] = True
                    break

        return context

#Class-based DetailView that handles, gathers the context for and renders a page for a particular television series crew (inherits from TVDetail)
class TVCrewDetailView(TVDetailView):
    template_name = 'media/tvCrewDetail.html'

#Class-based UpdateView that handles, gathers the context for and renders a page for a particular video game
class VideoGameDetailView(generic.UpdateView):
    model = VideoGame
    template_name = 'media/gameDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    #POST method to make a call to the mediaPagePostRequests handler
    def post(self, request, *args, **kwargs):
        mediaPagePostRequests(self, request, *args, **kwargs)
        return super(VideoGameDetailView, self).post(request, *args, **kwargs)

    # Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Retrieve the necessary context for the video game
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

        #Retrieve the parent franchise based on:
        #the videogame-franchisesubcategory mappings
        #and the videogame-videogamefranchisesubcategory mappings
        franchises = {}
        for x in VideoGameVideoGameFranchiseSubcategoryMapping.objects.filter(videoGame=self.object.id):
            if x.videoGame.id == self.object.id:
                franchises[x.videoGameFranchiseSubcategory.parentFranchise] = 'vgf'
        for x in VideoGameFranchiseSubcategoryMapping.objects.filter(videoGame=self.object.id):
            if x.videoGame.id == self.object.id:
                franchises[x.franchiseSubcategory.parentFranchise] = 'f'
        context['franchises'] = franchises

        #Retrieve the ratings for the video game
        ratings = VideoGameRating.objects.filter(videoGame=self.object.id)
        ratingCount = ratings.count()
        context['ratingCount'] = ratingCount
        if ratingCount > 0:
            ratingSum = 0
            for rating in ratings:
                ratingSum += rating.rating
            #Calculate the average rating for the film
            average = ratingSum/ratingCount
            averageRating = "{:.1f}".format(average)
            #Format the rating for the front-end
            context['averageRating'] = averageRating
            context['averageRatingText'] = "{:.1f}".format(float(averageRating)/2)

            #Attempt to retrieve the user's rating of the game
            if self.request.user.is_authenticated:
                r = VideoGameRating.objects.filter(user=self.request.user, videoGame=self.object.id).first()
                if r is not None:
                    context['userRating'] = r.rating
                    context['userRatingText'] = r.rating / 2
                    if r.review is not None:
                        context['review'] = r.review

        #Retrieve whether the game is in the user's list
        if self.request.user.is_authenticated:
            context['inList'] = False
            for listvg in UserListVideoGameMapping.objects.filter(user=self.request.user):
                if listvg.videoGame.id == self.object.id:
                    context['inList'] = True
                    break

        return context

#Class-based DetailView that handles, gathers the context for and renders a page for a particular video game crew
class VideoGameCrewDetailView(VideoGameDetailView):
    template_name = 'media/gameCrewDetail.html'

#Class-based UpdateView that handles, gathers the context for and renders a page for a particular book
class BookDetailView(generic.UpdateView):
    model = Book
    template_name = 'media/bookDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    #POST method to make a call to the mediaPagePostRequests handler
    def post(self, request, *args, **kwargs):
        mediaPagePostRequests(self, request, *args, **kwargs)
        return super(BookDetailView, self).post(request, *args, **kwargs)

    # Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Retrieve the necessary context
        context['genres'] = BookGenreMapping.objects.filter(book=self.object.id)
        context['authors'] = BookPersonMapping.objects.filter(role=3, book=self.object.id)
        context['publishers'] = BookCompanyMapping.objects.filter(role=5, book=self.object.id)

        #Retrieve the parent franchise based on the book-franchisesubcategory mapping
        franchises = []
        for x in BookFranchiseSubcategoryMapping.objects.filter(book=self.object.id):
            if x.book.id == self.object.id:
                franchises.append(x.franchiseSubcategory.parentFranchise)
        context['franchises'] = franchises

        #Retrieve the ratings for the book
        ratings = BookRating.objects.filter(book=self.object.id)
        ratingCount = ratings.count()
        context['ratingCount'] = ratingCount
        if ratingCount > 0:
            ratingSum = 0
            for rating in ratings:
                ratingSum += rating.rating
            #Calculate the average rating
            average = ratingSum/ratingCount
            #Format the rating for the front-end
            averageRating = "{:.1f}".format(average)
            context['averageRating'] = averageRating
            context['averageRatingText'] = "{:.1f}".format(float(averageRating)/2)

            #Attempt to retrieve the user's rating of the book
            if self.request.user.is_authenticated:
                r = BookRating.objects.filter(user=self.request.user, book=self.object.id).first()
                if r is not None:
                    context['userRating'] = r.rating
                    context['userRatingText'] = r.rating / 2

        #Retrieve whether the book is in the user's list or not
        if self.request.user.is_authenticated:
            context['inList'] = False
            for listb in UserListBookMapping.objects.filter(user=self.request.user):
                if listb.book.id == self.object.id:
                    context['inList'] = True
                    break

        return context

#Class-based UpdateView that handles, gathers the context for and renders a page for a particular web series
class WebSeriesDetailView(generic.UpdateView):
    model = WebSeries
    template_name = 'media/webDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"
    fields = []

    #POST method to make a call to the mediaPagePostRequests handler
    def post(self, request, *args, **kwargs):
        mediaPagePostRequests(self, request, *args, **kwargs)
        return super(WebSeriesDetailView, self).post(request, *args, **kwargs)

    # Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Retrieve the context
        context['genres'] = WebSeriesGenreMapping.objects.filter(webSeries=self.object.id).order_by('genre__title')
        context['cast'] = WebSeriesPersonMapping.objects.filter(role=1, webSeries=self.object.id).order_by('billing')
        context['showrunners'] = WebSeriesPersonMapping.objects.filter(role=4, webSeries=self.object.id)
        context['writers'] = WebSeriesPersonMapping.objects.filter(role=3, webSeries=self.object.id)
        context['producers'] = WebSeriesPersonMapping.objects.filter(role=6, webSeries=self.object.id)
        context['networks'] = WebSeriesCompanyMapping.objects.filter(role=3, webSeries=self.object.id)
        context['productionCompanies'] = WebSeriesCompanyMapping.objects.filter(role=2, webSeries=self.object.id)
        context['images'] = WebSeriesImages.objects.filter(webSeries=self.object.id)

        #Retrieve the parent franchise based on the webseries-franchisesubcategory mapping
        franchises = []
        for x in WebSeriesFranchiseSubcategoryMapping.objects.filter(webSeries=self.object.id):
            if x.webSeries.id == self.object.id:
                franchises.append(x.franchiseSubcategory.parentFranchise)
        context['franchises'] = franchises

        #Retrieve the ratings of this web series
        ratings = WebSeriesRating.objects.filter(webSeries=self.object.id)
        ratingCount = ratings.count()
        context['ratingCount'] = ratingCount
        if ratingCount > 0:
            ratingSum = 0
            for rating in ratings:
                ratingSum += rating.rating
            #Calculate the average rating of the web series
            average = ratingSum/ratingCount
            #Format the rating for the front-end
            averageRating = "{:.1f}".format(average)
            context['averageRating'] = averageRating
            context['averageRatingText'] = "{:.1f}".format(float(averageRating)/2)

            #Attempt to retrieve the user's rating of the web series
            if self.request.user.is_authenticated:
                r = WebSeriesRating.objects.filter(user=self.request.user, webSeries=self.object.id).first()
                if r is not None:
                    context['userRating'] = r.rating
                    context['userRatingText'] = r.rating / 2
                    if r.review is not None:
                        context['review'] = r.review

        #Retrieve whether the web series is in the user's list
        if self.request.user.is_authenticated:
            context['inList'] = False
            for listws in UserListWebSeriesMapping.objects.filter(user=self.request.user):
                if listws.webSeries.id == self.object.id:
                    context['inList'] = True
                    break

        return context

#Class-based DetailView that handles, gathers the context for and renders a page for a particular genre
class GenreDetailView(generic.DetailView):
    model = Genre
    template_name = 'media/genreDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"

    #Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Retrieve all of the data for the different horizontal sliders on the genre detail page
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

#Class-based DetailView that handles, gathers the context for and renders a page for a particular tag
class TagDetailView(generic.DetailView):
    model = Tag
    template_name = 'media/tagDetail.html'
    slug_field, slug_url_kwarg = "slug", "slug"

    #Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Retrieve all of the data for the different horizontal sliders on the genre detail page
        context['films'] = FilmTagMapping.objects.filter(tag=self.object.name)
        context['television'] = TelevisionTagMapping.objects.filter(tag=self.object.name)

        return context

#Class-based DetailView that handles, gathers the context for and renders a page for a particular video game genre
class VideoGameGenreDetailView(generic.DetailView):
    model = VideoGameGenre
    template_name = 'media/gameGenreDetail.html'

    #Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #Retrieve all of the data for the different horizontal sliders on the genre detail page
        context['franchises'] = VideoGameFranchiseGenreMapping.objects.filter(genre=self.object.id)
        context['projects'] = VideoGameGenreMapping.objects.filter(genre=self.object.id).order_by('videoGame__release')[:100]
        return context

#Class-based DetailView that handles, gathers the context for and renders a page for a particular console
class ConsoleDetailView(generic.DetailView):
    model = Console
    template_name = 'media/consoleDetail.html'

    #Method to set up the context data to pass to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        #Retrieve the featured video games for this particular console
        featured = []
        all = []
        for g in VideoGameConsoleMapping.objects.filter(console=self.object.id).order_by('videoGame__release'):
            if g.featured:
                featured.append(g)
            else:
                all.append(g)

        #Pass the games, featuredGames and various console versions to the context
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
