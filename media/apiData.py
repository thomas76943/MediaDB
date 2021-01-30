import requests, json, datetime
from django.core.files import File

def getFilms():

    ratingsFile = open("D:\MediaDB Datasets\movielensSmall\ratings.csv", "r")
    ratingsData = csv.reader(ratingsFile)

    people = Person.objects.all()
    genres = Genre.objects.all()


    films = Film.objects.all()
    filmTitles = []
    for film in films:
        filmTitles.append(film.title)



    """
    for row in ratingsData:
        resp = requests.get("http://www.omdbapi.com/?i=" + row + "&apikey=5cd5955c")
        data = json.loads(resp.text)
        if data['Title'] in titles:
            print("Skipped: ", data['Title'])

        else:
            print("Title - ", data['Title'], "\n")
            print("Release - ", data['Released'], "\n")
            print("Rating - ", data['Rated'], "\n")
            print("Synopsis - ", data['Plot'], "\n")
            print("Length - ", data['Runtime'][:-4], "\n")
            print("Budget - ", data['Plot'], "\n")


            f = Film(title=data['Title'], release="1999-01-01", length=data['Runtime'][:-4])
            img_data = requests.get(data['Poster']).content
            img_name = data['Title'] + "-" + str(data['Year']) + ".jpg"
            with open("D:/APITesting/"+img_name, 'wb') as handler:
                handler.write(img_data)

            f.poster.save(img_name, File(open("D:/API Testing/"+img_name, "rb")))
            f.save()
    """
