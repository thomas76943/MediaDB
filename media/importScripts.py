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