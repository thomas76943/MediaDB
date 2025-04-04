import requests
import json
from themoviedb import TMDb
from .models import *
from django.utils.text import slugify
from django.core.files import File

#Script to import films data
def addFilmRatings():
    pathToFilmsData = ""
    ratingsFile = open(pathToFilmsData, "rt")
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

                    #Removing parentheses or credits from names
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

                    #Removing parentheses or credits from names
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

#Script to import video games data
def addVideoGameData():
    badCharsTitles = ['/', '#', '"', '<', '>', '[', ']', '{', '}', '@']
    badCharsOther = ['/', '#', '"', '<', '>', '[', ']', '{', '}', '@']

    pathToVideoGameData = ""
    with open(pathToVideoGameData, "r", encoding="utf8") as f:
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

#Script to import books data
def addBookData():

    badCharsTitles = ['/', '"', '<', '>', '[', ']', '{', '}', '@', 'Ã', 'Â', '©', '¢', '€', 'ž', '¦', '¶', 'º']
    badCharsPeople = ['?', '/', '#', '!', '"', '<', '>', '[', ']', '{', '}', '(', ')', ':', ';', '@', 'Ã', 'Â', '©', '¢', '€', 'ž', '¦', '¶', 'º']

    pathToBookData = ""
    bookFile = open(pathToBookData, "rt", encoding='utf-8')
    bookData = csv.reader(bookFile)

    for row in bookData:

        bookTitles = []
        for book in Book.objects.all():
            bookTitles.append(book.title)

        peopleNames = []
        for p in Person.objects.all():
            peopleNames.append(p.getFullName())

        title = row[0]
        isbn = row[1]
        desc = row[2]
        image = row[3]
        authorsRaw = row[4]
        pages = row[5]
        fulldate = row[6]
        publishers = row[7]
        genreA = row[8]
        genreB = row[9]
        genreC = row[10]

        if len(title) > 0:
            if any(badChar in title for badChar in badCharsTitles):
                print("Skipped Book: ", title + " - bad title format")
                continue

        if len(fulldate) > 0:
            if '-' in str(fulldate):
                print("Skipped Book: ", title + " - bad date format")
                continue
            else:
                year = fulldate[-4:]

        if title not in bookTitles:
            newbook = Book(title=title)
            newbook.release = year
            newbook.save()

        getBook = Book.objects.filter(title=title).first()

        if len(isbn) > 0:
            getBook.isbn = isbn

        if len(desc) > 0:
            if any(badChar in desc for badChar in badCharsTitles):
                print("--------------------------------------------------------------------------------------")
                print("Skipped description: ", title)
            else:
                getBook.synopsis = desc

        if len(pages) > 0:
            if int(pages) > 0:
                getBook.pages = int(pages)


        if len(authorsRaw) > 0:
            authorsSplit = authorsRaw.split(',')

            for author in authorsSplit:

                if author[0] == " ":
                    author = author[1:]

                firstLastNames = re.sub(r" ?\([^)]+\)", "", author)

                if firstLastNames == "N/A":
                    continue

                if any(badChar in firstLastNames for badChar in badCharsPeople):
                    print("--------------------------------------------------------------------------------------")
                    print("Skipped Person: ", firstLastNames)
                    continue

                if firstLastNames not in peopleNames:
                    print("Adding new person:", firstLastNames)
                    newPerson = Person()
                    firstLastNames = firstLastNames.split()
                    newPerson.firstName = firstLastNames[0]
                    if len(firstLastNames) > 1:
                        combinedSurname = ""
                        for name in firstLastNames[1:]:
                            combinedSurname += name + " "
                        newPerson.surname = combinedSurname[:-1]
                    newPerson.save()
                    thisAuthor = newPerson
                else:
                    print("Getting Existing Author: ", firstLastNames)
                    firstLastNames = firstLastNames.split(" ", 1) #Only Separating First Name Out
                    thisAuthor = Person.objects.filter(firstName=firstLastNames[0], surname=firstLastNames[1])[0]

                authorRole = PersonRole.objects.filter(id=5)[0]

                #If mapping doesn't already exist
                query = BookPersonMapping.objects.filter(person=thisAuthor, book=getBook, role=authorRole)
                if not query:
                    bpm = BookPersonMapping(person=thisAuthor, book=getBook, role=authorRole)
                    bpm.save()
                else:
                    print(thisAuthor.getFullName(), "is already tied to", getBook, "in this role")


        if len(image) > 1:
            img_data = requests.get(image).content
            img_name = slugify(title + "-" + str(year) + ".jpg")
            with open("D:/MediaDB Datasets/bookPostersTemp/" + img_name, 'wb') as handler:
                handler.write(img_data)
            getBook.image.save(img_name, File(open("D:/MediaDB Datasets/bookPostersTemp/" + img_name, "rb")))


        if len(genreA) > 0:
            if genreA[0] == " ":
                genreA = genreA[1:]
            genreTitles = []
            for g in BookGenre.objects.all():
                genreTitles.append(g.title)
            if any(badChar in genreA for badChar in badCharsTitles):
                print("Skipped Genre: ", genreA)
            else:
                genreA = genreA.rpartition(" ")[0]
                if genreA not in genreTitles:
                    print(genreA)
                    newGenre = BookGenre(title=genreA)
                    newGenre.save()
                    genreTitles.append(newGenre)

                getGenre = BookGenre.objects.filter(title=genreA)[0]
                bgm = BookGenreMapping.objects.filter(book=getBook, genre=getGenre)
                if bgm:
                    print("This book already has this genre:", getGenre)
                else:
                    bgm = BookGenreMapping(book=getBook, genre=getGenre)
                    bgm.save()

        if len(genreB) > 0:
            if genreB[0] == " ":
                genreB = genreB[1:]
            genreTitles = []
            for g in BookGenre.objects.all():
                genreTitles.append(g.title)
            if any(badChar in genreB for badChar in badCharsTitles):
                print("Skipped Genre: ", genreB)
            else:
                genreB = genreB.rpartition(" ")[0]
                if genreB not in genreTitles:
                    newGenre = BookGenre(title=genreB)
                    newGenre.save()
                    genreTitles.append(newGenre)

                getGenre = BookGenre.objects.filter(title=genreB)[0]
                bgm = BookGenreMapping.objects.filter(book=getBook, genre=getGenre)
                if bgm:
                    print("This book already has this genre:", getGenre)
                else:
                    bgm = BookGenreMapping(book=getBook, genre=getGenre)
                    bgm.save()

        if len(genreC) > 0:
            if genreC[0] == " ":
                genreC = genreC[1:]
            genreTitles = []
            for g in BookGenre.objects.all():
                genreTitles.append(g.title)
            if any(badChar in genreC for badChar in badCharsTitles):
                print("Skipped Genre: ", genreC)
            else:
                genreC = genreC.rpartition(" ")[0]
                if genreC not in genreTitles:
                    newGenre = BookGenre(title=genreC)
                    newGenre.save()
                    genreTitles.append(newGenre)

                getGenre = BookGenre.objects.filter(title=genreC)[0]
                bgm = BookGenreMapping.objects.filter(book=getBook, genre=getGenre)
                if bgm:
                    print("This book already has this genre:", getGenre)
                else:
                    bgm = BookGenreMapping(book=getBook, genre=getGenre)
                    bgm.save()

        if len(publishers) > 0:
            companyTitles = []
            for c in Company.objects.all():
                companyTitles.append(c.name)

            publishersSplit = publishers.split(',')
            for publisher in publishersSplit:
                if any(badChar in publisher for badChar in badCharsTitles):
                    print("Skipped Publisher: ", publisher)
                else:
                    if publisher not in companyTitles:
                        newcomp = Company(name=publisher)
                        newcomp.save()

                    getcompany = Company.objects.filter(name=publisher).first()
                    publisherRole = CompanyRole.objects.filter(id=5)[0]

                    # If mapping doesn't already exist
                    query = BookCompanyMapping.objects.filter(company=getcompany, book=getBook, role=publisherRole)
                    if not query:
                        bcm = BookCompanyMapping(company=getcompany, book=getBook, role=publisherRole)
                        bcm.save()
                    else:
                        print(getcompany.name, "is already tied to", getBook, "in this role")

        getBook.save()


def addTMDBIDsToPeople():

    # new TMDB object
    tmdb = TMDb()
    tmdb.key = "519e516edf4f8f69710bded749a22ff7"

    pd = tmdb.person(id).details()

    #https://api.themoviedb.org/3/search/person?include_adult=false&query=matt damon&api_key=519e516edf4f8f69710bded749a22ff7



def addSmallImages():

    # create TMDb object and provide api_key
    tmdb = TMDb()
    tmdb.key = "519e516edf4f8f69710bded749a22ff7"

    for person in Person.objects.all():
        #print(person.image)
        if person.image != 'MissingIcon.png' and person.imageSmall == 'MissingIcon.png':

            pd = tmdb.person(person.tmdbid).details()
            print("Adding Small Image To:", person.getFullName())

            # add small image
            if pd.profile_path is not None and len(pd.profile_path) > 0:
                img_data = requests.get("https://image.tmdb.org/t/p/w342" + pd.profile_path).content
                img_name = slugify(person.getFullName() + "-" + str(person.tmdbid)) + "-w342.jpg"
                with open(
                        "D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name,
                        'wb') as handler:
                    handler.write(img_data)
                    person.imageSmall.save(img_name, File(open(
                        "D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name,
                        "rb")))


def resetSlugs():

    for ep in TelevisionEpisode.objects.all():
        ep.slug = ""
        ep.save()


def addTVNetworks():

    existingCompanies = []
    for company in Company.objects.all():
        existingCompanies.append(str(company.name))

    getNetworkRole = CompanyRole.objects.filter(id=9).first()


    tmdb = TMDb()
    tmdb.key = "519e516edf4f8f69710bded749a22ff7"

    for tv in Television.objects.all():

        tvd = tmdb.tv(tv.tmdbid).details()

        print("Found TV:", tvd.name)

        if tvd.networks is not None:

            print(tvd.networks)


            for network in tvd.networks:

                # retrieve company details from tmdb
                cd = tmdb.network(network.id).details()

                if str(cd.name) in existingCompanies:
                    print("Network:", cd.name, "--- already in db")
                    getCompany = Company.objects.filter(name=cd.name).first()
                else:
                    print("Network:", cd.name, "--- adding new company")
                    newCompany = Company(name=cd.name, tmdbid=network.id)
                    existingCompanies.append(str(cd.name))

                    if cd.logo_path is not None and len(cd.logo_path) > 1:
                        img_data = requests.get("https://image.tmdb.org/t/p/original" + cd.logo_path).content
                        img_name = slugify(cd.name + "-" + str(cd.id)) + ".png"
                        with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbCompanyDownloads/" + img_name,'wb') as handler:handler.write(img_data)
                        newCompany.image.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbCompanyDownloads/" + img_name,"rb")))

                    if cd.origin_country is not None and len(cd.origin_country) > 0:
                        newCompany.baseCountry = cd.origin_country

                    newCompany.save()
                    getCompany = newCompany

                tvcm = TelevisionCompanyMapping(television=tv, company=getCompany, role=getNetworkRole)
                tvcm.save()

        else:
            print("No Networks")

        print("")

def addTVData():

    # get tmdb IDs of all existing films in database
    existingTVIDs = []
    for tv in Television.objects.all():
        existingTVIDs.append(str(tv.tmdbid))

    # get names of all existing genres in database
    existingGenres = []
    for genre in Genre.objects.all():
        existingGenres.append(genre.title)

    # get tmdb IDs of all existing people in database
    existingPeopleIDs = []
    for person in Person.objects.all():
        existingPeopleIDs.append(str(person.tmdbid))

    # get list of all role types in database
    existingPeopleRoleTypes = []
    for role in PersonRole.objects.all():
        existingPeopleRoleTypes.append(role.role)

    # get tmdb IDs of all existing companies in database
    existingCompanies = []
    for company in Company.objects.all():
        existingCompanies.append(company.tmdbid)

    existingNetworks = []
    for network in Company.objects.all():
        existingNetworks.append(str(network.name))


    # get list of all existing tags in database
    existingTags = []
    for tag in Tag.objects.all():
        existingTags.append(tag.name)

    getActorRole = PersonRole.objects.filter(role="Actor").first()
    getCastDepartment = Department.objects.filter(department="Cast").first()
    getProductionCompanyRole = CompanyRole.objects.filter(id=7).first()
    getNetworkRole = CompanyRole.objects.filter(id=9).first()

    tmdb = TMDb()
    tmdb.key = "519e516edf4f8f69710bded749a22ff7"

    # mandalorian tvSingleTest = ['82856']
    # loki tvSingleTest = ['84958']
    # GoT tvSingleTest = ['1399']
    # daredevil = ['61889']
    # rickandmorty = ['60625']
    # wandavision = ['85271']

    for id in ['655']:

        #get film details based on tmdb-id
        tvd = tmdb.tv(id).details()

        # get details of film credits from tmdb
        tvc = tmdb.tv(id).credits()

        print("")
        print("Found TV:", tvd.name)

        if str(id) not in existingTVIDs:
            print("")
            print("Adding New TV:", tvd.name)
            newTV = Television(title=tvd.name)
            newTV.tmdbid = id
            newTV.release = tvd.first_air_date
            newTV.ongoing = tvd.in_production
            newTV.seasonCount = tvd.number_of_seasons
            newTV.episodeCount = tvd.number_of_episodes
            newTV.synopsis = tvd.overview
            newTV.save()

            # add show cover image
            if tvd.backdrop_path is not None and len(tvd.backdrop_path) > 1:
                print("Backdrop: https://image.tmdb.org/t/p/w1280" + tvd.backdrop_path)
                img_data = requests.get("https://image.tmdb.org/t/p/w1280" + tvd.backdrop_path).content
                img_name = slugify(tvd.name + "-" + str(tvd.id)) + "-cover.jpg"
                with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbTVCoverDownloads/" + img_name,'wb') as handler: handler.write(img_data)
                newTV.cover.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbTVCoverDownloads/" + img_name,"rb")))

            getTV = newTV
            print("")

        else:
            print("")
            print("TV Already in DB:", tvd.name)
            getTV = Television.objects.filter(tmdbid=id).first()

        #Aggregate Credits for Whole Show
        '''
        tvac = tmdb.tv(id).aggregate_credits()

        print("Aggregate Cast Credits:")
        for index,credit in enumerate(tvac.cast):
            roles = ""
            for idx,role in enumerate(credit.roles):
                if role.character != '':
                    roles += role.character
                    roles += ", "
            if roles != '':
                if roles[-2] == ',':
                    roles = roles[:-2]
            print("Index:", index, "- Name:", credit.name, "- Order:", credit.order, "- Ep Count:", credit.total_episode_count, "- Role:", roles)

            if index > 40:
                break
        
        print("")
        print("Aggregate Crew Credits:")
        #print(tvac.crew)
        for index, credit in enumerate(tvac.crew):
            jobs = ""
            for idx, job in enumerate(credit.jobs):
                    jobs += job.job
                    jobs += ", "
            if jobs != '':
                if jobs[-2] == ',':
                    jobs = jobs[:-2]

            print("Index:", index, "- Job:", jobs, " - Name:", credit.name, "- Order:", credit.order, "- Ep Count:", credit.total_episode_count)

            if index > 10:
                break
        '''

        # get keywords from tmdb
        tvkeywords = tmdb.tv(id).keywords()
        if tvkeywords is not None:
            for keyword in tvkeywords:
                # if tag already in the database, get existing tag object

                if keyword.name in existingTags:
                    getTag = Tag.objects.filter(name=keyword).first()
                    print(keyword, "- already got this tag. Got here 1")
                # otherwise create new tag object
                else:
                    newTag = Tag(name=keyword)
                    newTag.save()
                    print(keyword, "- added new tag. Got here 2")
                    existingTags.append(keyword)
                    getTag = newTag

                tvtm = TelevisionTagMapping(television=getTV, tag=getTag)
                tvtm.save()
                
        if tvd.genres is not None and len(tvd.genres) > 0:
            # for each new genre
            for genre in tvd.genres:
                # if genre already in the database, get existing genre object
                if genre.name in existingGenres:
                    getGenre = Genre.objects.filter(title=genre.name).first()
                    print(genre, "- already got this genre")
                # otherwise create new genre object
                else:
                    newGenre = Genre(title=genre.name)
                    newGenre.save()
                    print(genre, "- added new genre")
                    existingGenres.append(genre.name)
                    getGenre = newGenre

                # add Film-Genre mappings
                tvgm = TelevisionGenreMapping(television=getTV, genre=getGenre)
                tvgm.save()
        
        
        
        # if Film-Company mappings exist in tmdb (for production companies)
        if tvd.production_companies is not None:

            # for each production company
            for pc in tvd.production_companies:

                # retrieve company details from tmdb
                cd = tmdb.company(pc.id).details()

                if str(cd.id) in existingCompanies:
                    print("Production Company:", cd.name, "--- already in db")
                    getCompany = Company.objects.filter(tmdbid=cd.id).first()
                else:
                    print("Production Company:", cd.name, "--- adding new company")
                    newCompany = Company(name=cd.name, tmdbid=cd.id)
                    existingCompanies.append(str(cd.id))

                    if cd.logo_path is not None and len(cd.logo_path) > 1:
                        img_data = requests.get("https://image.tmdb.org/t/p/original" + cd.logo_path).content
                        img_name = slugify(cd.name + "-" + str(cd.id)) + ".png"
                        with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbCompanyDownloads/" + img_name,'wb') as handler:handler.write(img_data)
                        newCompany.image.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbCompanyDownloads/" + img_name,"rb")))

                    if cd.origin_country is not None and len(cd.origin_country) > 0:
                        newCompany.baseCountry = cd.origin_country

                    if cd.description is not None and len(cd.description) > 0:
                        newCompany.description = cd.description

                    newCompany.save()
                    getCompany = newCompany

                tvcm = TelevisionCompanyMapping(television=getTV, company=getCompany, role=getProductionCompanyRole)
                tvcm.save()
        else:
            print("No Production Companies")


        # if Film-Company mappings exist in tmdb (for networks)
        if tvd.networks is not None:

            # for each network
            for network in tvd.networks:

                # retrieve company details from tmdb
                cd = tmdb.network(network.id).details()

                if str(cd.name) in existingNetworks:
                    print("Network:", cd.name, "--- already in db")
                    getCompany = Company.objects.filter(name=cd.name).first()
                else:
                    print("Network:", cd.name, "--- adding new company")
                    newCompany = Company(name=cd.name, tmdbid=network.id)
                    existingCompanies.append(str(cd.name))

                    if cd.logo_path is not None and len(cd.logo_path) > 1:
                        img_data = requests.get("https://image.tmdb.org/t/p/original" + cd.logo_path).content
                        img_name = slugify(cd.name + "-" + str(cd.id)) + ".png"
                        with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbCompanyDownloads/" + img_name,'wb') as handler:handler.write(img_data)
                        newCompany.image.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbCompanyDownloads/" + img_name,"rb")))

                    if cd.origin_country is not None and len(cd.origin_country) > 0:
                        newCompany.baseCountry = cd.origin_country

                    newCompany.save()
                    getCompany = newCompany

                tvcm = TelevisionCompanyMapping(television=getTV, company=getCompany, role=getNetworkRole)
                tvcm.save()

        else:
            print("No Networks")


        # get all existing seasons in the db for this show
        getExistingSeasons = []
        for s in TelevisionSeason.objects.filter(televisionSeries=getTV):
            getExistingSeasons.append(str(s.tmdbid))


        # for each season in tv show
        for season in tvd.seasons:

            seasonDetails = tmdb.season(tv_id=id, season_id=season.season_number).details()

            # if season not already in db, add new season
            if str(season.id) not in getExistingSeasons:

                print("")
                print("Adding New Season:")
                print("Season Name:", season.name)
                print("Season Number:", season.season_number)
                print("Season Episode Count:", season.episode_count)
                if season.poster_path is not None:
                    print("Season Poster: https://image.tmdb.org/t/p/w780" + season.poster_path)
                print("Season Overview:", seasonDetails.overview)
                print("")

                newSeason = TelevisionSeason(televisionSeries=getTV, seasonNumber=season.season_number, episodeCount=season.episode_count)

                newSeason.tmdbid = seasonDetails.id
                newSeason.release = seasonDetails.air_date

                if seasonDetails.name is not None and len(seasonDetails.name) > 0:
                    newSeason.title = seasonDetails.name

                if seasonDetails.overview is not None and len(seasonDetails.overview) > 0:
                    newSeason.synopsis = seasonDetails.overview

                newSeason.save()

                # add season poster images
                if season.poster_path is not None and len(season.poster_path) > 1:

                    # save full size poster image
                    img_data = requests.get("https://image.tmdb.org/t/p/w780" + season.poster_path).content
                    img_name = slugify(tvd.name + "-" + str(tvd.id) + "-s" + str(season.season_number)) + "-poster-w780.jpg"
                    with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbTVPosterDownloads/" + img_name,'wb') as handler: handler.write(img_data)
                    newSeason.poster.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbTVPosterDownloads/" + img_name,"rb")))

                    # save small poster image
                    img_data = requests.get("https://image.tmdb.org/t/p/w342" + season.poster_path).content
                    img_name = slugify(tvd.name + "-" + str(tvd.id) + "-s" + str(season.season_number)) + "-poster-w342.jpg"
                    with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbTVPosterDownloadsSmall/" + img_name,'wb') as handler: handler.write(img_data)
                    newSeason.posterSmall.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbTVPosterDownloadsSmall/" + img_name,"rb")))

                getSeason = newSeason

            else:
                print("")
                print("Already Got This Season: S" + str(season.season_number))
                getSeason = TelevisionSeason.objects.filter(tmdbid=season.id).first()

            print("")

            # get all existing episodes in the db for this season
            getExistingEpisodes = []
            for e in TelevisionEpisode.objects.filter(televisionSeason=getSeason):
                getExistingEpisodes.append(str(e.tmdbid))


            # for each episode in season
            for episode in seasonDetails.episodes:

                if episode.air_date is not None:
                        #and season.season_number == 6 and episode.episode_number in (15,16,17,18,19,20,21,22,23,24)):

                    episodeDetails = tmdb.episode(tv_id=id, season_id=season.season_number,episode_id=episode.episode_number).details()
                    episodeCredits = tmdb.episode(tv_id=id, season_id=season.season_number,episode_id=episode.episode_number).credits()
                    episodeGuestStars = episodeDetails.guest_stars
                    episodeCrew = episodeDetails.crew

                    # if episode not already in db, add new episode
                    if str(episode.id) not in getExistingEpisodes:

                        print("          Adding New Episode")
                        print("          Episode ID:", episode.id)
                        print("          Episode Name:", episode.name, "---", "S" + str(season.season_number) + "E" + str(episode.episode_number))
                        print("          Episode Runtime:", episode.runtime)
                        print("          Episode Air Date:", episode.air_date)
                        print("          Episode Overview:", episode.overview)

                        newEpisode = TelevisionEpisode(televisionSeason=getSeason)
                        newEpisode.tmdbid = episode.id
                        newEpisode.title = episode.name
                        newEpisode.episodeNumber = episode.episode_number
                        newEpisode.release = episode.air_date
                        newEpisode.save()

                        # add show cover image
                        if episode.still_path is not None and len(episode.still_path) > 1:
                            print("          Still: https://image.tmdb.org/t/p/w780" + episode.still_path)
                            img_data = requests.get("https://image.tmdb.org/t/p/w780" + episode.still_path).content
                            img_name = slugify(tvd.name + "-" + str(tvd.id) + "-s" + str(season.season_number) + "e" + str(episode.episode_number)) + "-still-w780.jpg"
                            with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbTVCoverDownloads/" + img_name,'wb') as handler: handler.write(img_data)
                            newEpisode.stillImage.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbTVCoverDownloads/" + img_name,"rb")))

                        print("")

                        getEpisode = newEpisode

                    else:
                        print("Already Got This Episode: S" + str(season.season_number) + "-E" + str(episode.episode_number))
                        getEpisode = TelevisionEpisode.objects.filter(tmdbid=episode.id).first()


                    # test with only 1 episode

                    print("Episode Crew:",)
                    for index, credit in enumerate(episodeCrew):

                        pd = tmdb.person(credit.id).details()

                        if str(credit.id) in existingPeopleIDs:
                            print(credit.job, "- credit id:", credit.id, "- credit name:", credit.name, "already in db")
                            getPerson = Person.objects.filter(tmdbid=credit.id).first()

                        else:
                            print(credit.job, "- credit id:", credit.id, "- credit name:", credit.name, "adding new person")
                            newPerson = Person(name=credit.name, DoB=pd.birthday, tmdbid=credit.id)
                            existingPeopleIDs.append(str(credit.id))

                            if pd.profile_path is not None and len(pd.profile_path) > 1:
                                # add full-size image
                                img_data = requests.get("https://image.tmdb.org/t/p/original" + pd.profile_path).content
                                img_name = slugify(credit.name + "-" + str(credit.id)) + ".jpg"
                                with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloads/" + img_name,'wb') as handler:handler.write(img_data)
                                newPerson.image.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloads/" + img_name,"rb")))

                                # add small image
                                img_data = requests.get("https://image.tmdb.org/t/p/w342" + pd.profile_path).content
                                img_name = slugify(credit.name + "-" + str(credit.id)) + "-w342.jpg"
                                with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name,'wb') as handler:handler.write(img_data)
                                newPerson.imageSmall.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name,"rb")))

                            if pd.deathday is not None:
                                newPerson.DoD = pd.deathday
                                newPerson.alive = False

                            newPerson.save()
                            getPerson = newPerson

                        # create new film-person mapping
                        tpm = TelevisionEpisodePersonMapping(televisionEpisode=getEpisode, person=getPerson)

                        getDepartment = Department.objects.filter(department=credit.department).first()

                        if credit.job in existingPeopleRoleTypes:
                            getRole = PersonRole.objects.filter(role=credit.job).first()
                        else:
                            newRole = PersonRole(role=credit.job)
                            newRole.save()
                            existingPeopleRoleTypes.append(credit.job)
                            getRole = newRole

                        tpm.department = getDepartment
                        tpm.role = getRole
                        tpm.save()




                    print("")
                    print("Series Cast:",)
                    for index, credit in enumerate(episodeCredits.cast):

                        pd = tmdb.person(credit.id).details()

                        if str(credit.id) in existingPeopleIDs:
                            print("Actor:", credit.name, "- Character:", credit.character, "- Billing Order:", credit.order, "- already in db")
                            getPerson = Person.objects.filter(tmdbid=credit.id).first()
                        else:
                            print("Actor:", credit.name, "- Character:", credit.character, "- Billing Order:", credit.order, "- ADDING NEW PERSON")
                            newPerson = Person(name=credit.name, DoB=pd.birthday, tmdbid=credit.id)
                            existingPeopleIDs.append(str(credit.id))

                            if pd.profile_path is not None and len(pd.profile_path) > 1:
                                # add full-size image
                                img_data = requests.get("https://image.tmdb.org/t/p/w500" + pd.profile_path).content
                                img_name = slugify(credit.name + "-" + str(credit.id)) + "-w500.jpg"
                                with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloads/" + img_name,'wb') as handler:handler.write(img_data)
                                newPerson.image.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloads/" + img_name,"rb")))

                                # add small image
                                img_data = requests.get("https://image.tmdb.org/t/p/w342" + pd.profile_path).content
                                img_name = slugify(credit.name + "-" + str(credit.id)) + "-w342.jpg"
                                with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name,'wb') as handler:handler.write(img_data)
                                newPerson.imageSmall.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name,"rb")))

                            if pd.deathday is not None:
                                newPerson.DoD = pd.deathday
                                newPerson.alive = False

                            newPerson.save()
                            getPerson = newPerson

                        tpm = TelevisionEpisodePersonMapping(televisionEpisode=getEpisode, person=getPerson, role=getActorRole, department=getCastDepartment)

                        if credit.character is not None and len(credit.character) > 0:
                            tpm.character = credit.character
                        if credit.order is not None:
                            tpm.billing = credit.order

                        tpm.save()


                    print("")
                    print("Guest Cast:")
                    for index, credit in enumerate(episodeGuestStars):

                        pd = tmdb.person(credit.id).details()

                        if str(credit.id) in existingPeopleIDs:
                            print("Actor:", credit.name, "- Character:", credit.character, "- Billing Order:", credit.order, "- already in db")
                            getPerson = Person.objects.filter(tmdbid=credit.id).first()
                        else:
                            print("Actor:", credit.name, "- Character:", credit.character, "- Billing Order:", credit.order, "- ADDING NEW PERSON")
                            newPerson = Person(name=credit.name, DoB=pd.birthday, tmdbid=credit.id)
                            existingPeopleIDs.append(str(credit.id))

                            if pd.profile_path is not None and len(pd.profile_path) > 1:
                                # add full-size image
                                img_data = requests.get("https://image.tmdb.org/t/p/w500" + pd.profile_path).content
                                img_name = slugify(credit.name + "-" + str(credit.id)) + "-w500.jpg"
                                with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloads/" + img_name,'wb') as handler:handler.write(img_data)
                                newPerson.image.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloads/" + img_name,"rb")))

                                # add small image
                                img_data = requests.get("https://image.tmdb.org/t/p/w342" + pd.profile_path).content
                                img_name = slugify(credit.name + "-" + str(credit.id)) + "-w342.jpg"
                                with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name,'wb') as handler:handler.write(img_data)
                                newPerson.imageSmall.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name,"rb")))

                            if pd.deathday is not None:
                                newPerson.DoD = pd.deathday
                                newPerson.alive = False

                            newPerson.save()
                            getPerson = newPerson

                        tpm = TelevisionEpisodePersonMapping(televisionEpisode=getEpisode, person=getPerson, role=getActorRole, department=getCastDepartment)

                        if credit.character is not None and len(credit.character) > 0:
                            tpm.character = credit.character
                        if credit.order is not None:
                            tpm.billing = credit.order

                        tpm.save()



def addTMDBData():

    badCharsTitles = ['/', '"', '<', '>', '[', ']', '{', '}', '@', 'Ã', 'Â', '©', '¢', '€', 'ž', '¦', '¶', 'º']
    badCharsPeople = ['?', '/', '#', '!', '"', '<', '>', '[', ']', '{', '}', '(', ')', ':', ';', '@', 'Ã', 'Â', '©', '¢', '€', 'ž', '¦', '¶', 'º']

    # get tmdb IDs of all existing films in database
    existingFilmIDs = []
    for film in Film.objects.all():
        existingFilmIDs.append(str(film.tmdbid))

    # get names of all existing genres in database
    existingGenres = []
    for genre in Genre.objects.all():
        existingGenres.append(genre.title)

    # get tmdb IDs of all existing people in database
    existingPeopleIDs = []
    for person in Person.objects.all():
        existingPeopleIDs.append(str(person.tmdbid))
    #print("existing people IDs:", existingPeopleIDs)

    # get list of all role types in database
    existingPeopleRoleTypes = []
    for role in PersonRole.objects.all():
        existingPeopleRoleTypes.append(role.role)

    # get tmdb IDs of all existing companies in database
    existingCompanies = []
    for company in Company.objects.all():
        existingCompanies.append(company.tmdbid)
    #print(existingCompanies)

    # get list of all existing tags in database
    existingTags = []
    for tag in Tag.objects.all():
        existingTags.append(tag.name)

    getActorRole = PersonRole.objects.filter(role="Actor").first()
    getCastDepartment = Department.objects.filter(department="Cast").first()
    getProductionCompanyRole = CompanyRole.objects.filter(id=7).first()

    # create TMDb object and provide api_key
    tmdb = TMDb()
    tmdb.key = "519e516edf4f8f69710bded749a22ff7"


    filmIDs = ['516729']


    for id in filmIDs:

        print("\n Attempting Film:", id)

        #get film details based on tmdb-id
        md = tmdb.movie(id).details()

        # get details of film credits from tmdb
        mc = tmdb.movie(id).credits()

        # get keywords from tmdb
        keywords = tmdb.movie(id).keywords()

        print("Found:", md.title, "---", md.release_date)

        # if the film is not in the database
        if id not in existingFilmIDs:

            # add title, release date and tmdb-id
            newFilm = Film(title=md.title)
            newFilm.release = md.release_date
            newFilm.tmdbid = id

            # add runtime
            if md.runtime is not None and md.runtime > 0:
                newFilm.length = md.runtime

            # add synopsis
            if md.overview is not None and len(md.overview) > 0:
                newFilm.synopsis = md.overview

            # add budget
            if md.budget is not None and int(md.budget) != 0:
                newFilm.budget = md.budget

            # add box office revenue
            if md.revenue is not None and int(md.revenue) != 0:
                newFilm.boxOffice = md.revenue

            # add poster image
            if md.poster_path is not None and len(md.poster_path) > 1:
                print("Poster: https://image.tmdb.org/t/p/original" + md.poster_path)

                # save full size poster image
                img_data = requests.get("https://image.tmdb.org/t/p/original" + md.poster_path).content
                img_name = slugify(md.title + "-" + str(md.release_date)) + "-poster.jpg"
                with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPosterDownloads/" + img_name, 'wb') as handler:
                    handler.write(img_data)
                newFilm.poster.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPosterDownloads/" + img_name, "rb")))

                # save small poster image
                img_data = requests.get("https://image.tmdb.org/t/p/w342" + md.poster_path).content
                img_name = slugify(md.title + "-" + str(md.release_date)) + "-poster-w342.jpg"
                with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPosterDownloadsSmall/" + img_name, 'wb') as handler:
                    handler.write(img_data)
                newFilm.posterSmall.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPosterDownloadsSmall/" + img_name, "rb")))

            # add cover image
            if md.backdrop_path is not None and len(md.backdrop_path) > 1:
                print("Backdrop: https://image.tmdb.org/t/p/w1280" + md.backdrop_path)
                img_data = requests.get("https://image.tmdb.org/t/p/w1280" + md.backdrop_path).content
                img_name = slugify(md.title + "-" + str(md.release_date)) + "-cover.jpg"
                with open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbCoverDownloads/" + img_name, 'wb') as handler:
                    handler.write(img_data)
                    newFilm.cover.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbCoverDownloads/" + img_name, "rb")))

            # save new film
            newFilm.save()
            getFilm = newFilm
            existingFilmIDs.append(id)

        # else retrieve the film if it already exists in the database
        else:
            getFilm = Film.objects.filter(tmdbid=id).first()


        # if there are no Film-Genre mappings for this film
        if not FilmGenreMapping.objects.filter(film=getFilm):
            # if Film-Genre mappings exist in tmdb
            if md.genres is not None and len(md.genres) > 0:
                # for each new genre
                for genre in md.genres:
                    # if genre already in the database, get existing genre object
                    if genre.name in existingGenres:
                        getGenre = Genre.objects.filter(title=genre.name).first()
                        print(genre, "- already got this genre")
                    # otherwise create new genre object
                    else:
                        newGenre = Genre(title=genre.name)
                        newGenre.save()
                        print(genre, "- added new genre")
                        existingGenres.append(genre.name)
                        getGenre = newGenre

                    # add Film-Genre mappings
                    fgm = FilmGenreMapping(film=getFilm, genre=getGenre)
                    fgm.save()
        else:
            "Film-Genre Mappings Already in Database"


        # if there are no Film-Company mappings for this film
        if not FilmCompanyMapping.objects.filter(film=getFilm):

            # if Film-Company mappings exist in tmdb
            if md.production_companies is not None:

                # add Film-Company mappings
                for pc in md.production_companies:

                    # retrieve company details from tmdb
                    cd = tmdb.company(pc.id).details()

                    if str(cd.id) in existingCompanies:
                        print("Production Company:", cd.name, "--- already in db")
                        getCompany = Company.objects.filter(tmdbid=cd.id).first()
                    else:
                        print("Production Company:", cd.name, "--- adding new company")
                        newCompany = Company(name=cd.name, tmdbid=cd.id)
                        existingCompanies.append(str(cd.id))

                        if cd.logo_path is not None and len(cd.logo_path) > 1:
                            img_data = requests.get("https://image.tmdb.org/t/p/original" + cd.logo_path).content
                            img_name = slugify(cd.name + "-" + str(cd.id)) + ".png"
                            with open(
                                "D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbCompanyDownloads/" + img_name,'wb') as handler:
                                handler.write(img_data)
                                newCompany.image.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbCompanyDownloads/" + img_name, "rb")))

                        if cd.origin_country is not None and len(cd.origin_country) > 0:
                            newCompany.baseCountry = cd.origin_country

                        if cd.description is not None and len(cd.description) > 0:
                            newCompany.description = cd.description

                        newCompany.save()
                        getCompany = newCompany

                    fcm = FilmCompanyMapping(film=getFilm, company=getCompany, role=getProductionCompanyRole)
                    fcm.save()
        else:
            "Film-Company Mappings Already in Database"


        # if there are no Film-Person mappings for this film
        if not FilmPersonMapping.objects.filter(film=getFilm):
            # if Film-Person (cast) mappings exist in tmdb
            if mc.cast is not None:
                # add Film-Person (cast) mappings
                for index,credit in enumerate(mc.cast):
                    # retrieve person details from tmdb
                    pd = tmdb.person(credit.id).details()

                    if str(credit.id) in existingPeopleIDs:
                        print("Actor:", credit.name, "- Character:", credit.character, "- Billing Order:", credit.order, "- already in db")
                        getPerson = Person.objects.filter(tmdbid=credit.id).first()

                    else:
                        print("Actor:", credit.name, "- Character:", credit.character, "- Billing Order:", credit.order, "- adding new person")
                        newPerson = Person(name=credit.name, DoB=pd.birthday, tmdbid=credit.id)
                        existingPeopleIDs.append(str(credit.id))

                        if pd.profile_path is not None and len(pd.profile_path) > 1:
                            # add full-size image
                            img_data = requests.get("https://image.tmdb.org/t/p/original" + pd.profile_path).content
                            img_name = slugify(credit.name + "-" + str(credit.id)) + ".jpg"
                            with open(
                                "D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloads/" + img_name,'wb') as handler:
                                handler.write(img_data)
                                newPerson.image.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloads/" + img_name, "rb")))

                            # add small image
                            img_data = requests.get("https://image.tmdb.org/t/p/w342" + pd.profile_path).content
                            img_name = slugify(credit.name + "-" + str(credit.id)) + "-w342.jpg"
                            with open(
                                "D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name,'wb') as handler:
                                handler.write(img_data)
                                newPerson.imageSmall.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name, "rb")))


                        if pd.deathday is not None:
                            newPerson.DoD = pd.deathday
                            newPerson.alive = False

                        newPerson.save()
                        getPerson = newPerson

                    fpm = FilmPersonMapping(film=getFilm, person=getPerson, role=getActorRole, department=getCastDepartment)

                    if credit.character is not None and len(credit.character) > 0:
                        fpm.character = credit.character
                    if credit.order is not None:
                        fpm.billing = credit.order

                    fpm.save()

            if mc.crew is not None:

                # adding credits for directors, writers and producers and rest of the crew
                for index,credit in enumerate(mc.crew):
                    pd = tmdb.person(credit.id).details()

                    if str(credit.id) in existingPeopleIDs:
                        print(credit.job, "- credit id:", credit.id, "- credit name:", credit.name, "already in db")
                        getPerson = Person.objects.filter(tmdbid=credit.id).first()

                    else:
                        print(credit.job, "- credit id:", credit.id, "- credit name:", credit.name, "adding new person")
                        newPerson = Person(name=credit.name, DoB=pd.birthday, tmdbid=credit.id)
                        existingPeopleIDs.append(str(credit.id))

                        if pd.profile_path is not None and len(pd.profile_path) > 1:
                            # add full-size image
                            img_data = requests.get("https://image.tmdb.org/t/p/original" + pd.profile_path).content
                            img_name = slugify(credit.name + "-" + str(credit.id)) + ".jpg"
                            with open(
                                "D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloads/" + img_name,'wb') as handler:
                                handler.write(img_data)
                                newPerson.image.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloads/" + img_name, "rb")))

                            # add small image
                            img_data = requests.get("https://image.tmdb.org/t/p/w342" + pd.profile_path).content
                            img_name = slugify(credit.name + "-" + str(credit.id)) + "-w342.jpg"
                            with open(
                                "D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name,'wb') as handler:
                                handler.write(img_data)
                                newPerson.imageSmall.save(img_name, File(open("D:/Django Projects/Media Database Website/MediaDB Datasets/tmdbPeopleDownloadsSmall/" + img_name, "rb")))

                        if pd.deathday is not None:
                            newPerson.DoD = pd.deathday
                            newPerson.alive = False

                        newPerson.save()
                        getPerson = newPerson

                    # create new film-person mapping
                    fpm = FilmPersonMapping(film=getFilm, person=getPerson)

                    getDepartment = Department.objects.filter(department=credit.department).first()

                    if credit.job in existingPeopleRoleTypes:
                        getRole = PersonRole.objects.filter(role=credit.job).first()
                    else:
                        newRole = PersonRole(role=credit.job)
                        newRole.save()
                        existingPeopleRoleTypes.append(credit.job)
                        getRole = newRole

                    fpm.department = getDepartment
                    fpm.role = getRole
                    fpm.save()

        else:
            "Film-Person Mappings Already in Database"


        # if there are no Film-Tag mappings for this film
        if not FilmTagMapping.objects.filter(film=getFilm).exists():

            # if Film-Keyword (tag) mappings exist in tmdb
            if keywords is not None:

                for keyword in keywords:
                    # if tag already in the database, get existing tag object
                    if keyword in existingTags:
                        getTag = Tag.objects.filter(name=keyword).first()
                        print(keyword, "- already got this tag")
                    # otherwise create new tag object
                    else:
                        newTag = Tag(name=keyword)
                        newTag.save()
                        print(keyword, "- added new tag")
                        existingGenres.append(keyword)
                        getTag = newTag

                    ftm = FilmTagMapping(film=getFilm, tag=getTag)
                    ftm.save()
