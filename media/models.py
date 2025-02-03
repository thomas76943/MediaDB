from PIL import Image
from django.db import models
from django.utils import timezone
from django.contrib.staticfiles.urls import static
from django.utils.text import slugify


#---People and Roles---------------------------------------------------------------------------------------------------#
class Person(models.Model):
    name = models.CharField(max_length=500, default='NoFirstNameSpecified')
    DoB = models.DateField(blank=True, null=True)
    alive = models.BooleanField(default=True)
    DoD = models.DateField(blank=True, null=True)
    bio = models.CharField(max_length=1000, default='', blank=True)
    image = models.ImageField(default='MissingIcon.png', upload_to='peopleImages', blank=True)
    imageSmall = models.ImageField(default='MissingIcon.png', upload_to='peopleImages', blank=True, null=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)
    tmdbid = models.CharField(max_length=20,null=True,blank=True,editable=True)

    def __str__(self):
        return (self.name)

    #Method to Get the person's full name
    def getFullName(self):
        return (self.name)

    #Overwritten save method to populate the slugfield based on the name and DoB of the person
    def save(self, *args, **kwargs):
        super().save()
        if not self.slug:
            if self.DoB:
                self.slug = slugify(self.getFullName() + "-" + str(self.tmdbid))
            else:
                self.slug = slugify(self.getFullName())
        super(Person, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"

class PersonRole(models.Model):
    role = models.CharField(max_length=500, default='NoRoleNameSpecified')

    def __str__(self):
        return self.role

    class Meta:
        verbose_name = "Person - Role Type"
        verbose_name_plural = "People - Role Types"


class Department(models.Model):#
    department = models.CharField(max_length=500, default='NoDepartmentNameSpecified')

    def __str__(self):
        return self.department
    class Meta:
        verbose_name = "Person - Department"
        verbose_name_plural = "People - Departments"

#---Companies and Roles------------------------------------------------------------------------------------------------#
class Company(models.Model):
    name = models.CharField(max_length=500, default='NoCompanyNameSpecified')
    baseCountry = models.CharField(max_length=500, blank=True)
    dateFounded = models.DateField(blank=True, null=True)
    description = models.CharField(max_length=2000, blank=True)
    parentCompany = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True, editable=True)
    image = models.ImageField(upload_to='companyLogos', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)
    tmdbid = models.CharField(max_length=20, blank=True, editable=True)

    def __str__(self):
        return self.name

    #Overwritten save method to populate the slugfield based on the company's name
    def save(self, *args, **kwargs):
        super().save()
        if not self.slug:
            self.slug = slugify(self.name)
        super(Company, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

class CompanyRole(models.Model):
    companyRoleName = models.CharField(max_length=500, default='NoCompanyRoleNameSpecified')

    def __str__(self):
        return self.companyRoleName

    class Meta:
        verbose_name = "Company - Role Type"
        verbose_name_plural = "Companies - Role Types"

#---Media Types: Film, Television, Video Games, Books, Web Series------------------------------------------------------#
class Film(models.Model):
    title = models.CharField(max_length=150, default='NoFilmTitleSpecified')
    release = models.DateField(default=timezone.now)
    length = models.IntegerField(null=True, blank=True)
    rating = models.CharField(max_length=10, blank=True)
    synopsis = models.CharField(max_length=500, blank=True)
    budget = models.IntegerField(null=True, blank=True)
    boxOffice = models.IntegerField(null=True, blank=True)
    poster = models.ImageField(upload_to='filmPosters', blank=True)
    posterSmall = models.ImageField(upload_to='filmPosters', null=True, blank=True)
    cover = models.ImageField(upload_to='filmCoverImages', blank=True)
    trailerVideoPath = models.CharField(max_length=500, blank=True)
    slug = models.SlugField(max_length=150, null=True, blank=True, editable=True)
    tmdbid = models.CharField(max_length=20,null=True,blank=True,editable=True)

    #Overwritten save method to populate the slugfield based on the film's title and release date
    def save(self, *args, **kwargs):
        super().save()
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(self.release))
        super(Film, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    #Gets the year of the film's release
    def getYear(self):
        return self.release.year

    def get_absolute_url(self):
        return ''

    class Meta:
        verbose_name = "Film"
        verbose_name_plural = "Films"

class Television(models.Model):
    title = models.CharField(max_length=500, default='NoTelevisionTitleSpecified')
    release = models.DateField(default=timezone.now)
    ongoing = models.BooleanField(default=False)
    synopsis = models.CharField(max_length=500, default='', blank=True)
    seasonCount = models.IntegerField(default=1, null=True, blank=True)
    episodeCount = models.IntegerField(default=1, null=True, blank=True)
    poster = models.ImageField(default='', upload_to='televisionPosters', null=True, blank=True)
    posterSmall = models.ImageField(default='', upload_to='televisionPosters', null=True, blank=True)
    cover = models.ImageField(default='', upload_to='televisionCoverImages', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)
    tmdbid = models.CharField(max_length=20,null=True,blank=True,editable=True)

    #Overwritten save method to populate the slugfield based on the television series' title and release date
    def save(self, *args, **kwargs):
        super().save()
        if not self.slug:
            self.slug = slugify(self.title + "-" + self.tmdbid)
        super(Television, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def getPoster(self):
        getSeason = TelevisionSeason.objects.filter(televisionSeries=self,seasonNumber=1).first()
        return getSeason.poster.url

    def getFirstAirDate(self):
        getSeasonOne = TelevisionSeason.objects.filter(televisionSeries=self, seasonNumber=1).first()
        getEpisodeOne = TelevisionEpisode.objects.filter(televisionSeason=getSeasonOne, episodeNumber=1).first()
        return getSeasonOne.release

    def getStartingYear(self):
        getSeasonOne = TelevisionSeason.objects.filter(televisionSeries=self, seasonNumber=1).first()
        getEpisodeOne = TelevisionEpisode.objects.filter(televisionSeason=getSeasonOne, episodeNumber=1).first()
        return getSeasonOne.release.year

    def getEndingYear(self):
        getLastSeason = TelevisionSeason.objects.filter(televisionSeries=self).order_by('-seasonNumber').first()
        getLastEpisode = TelevisionEpisode.objects.filter(televisionSeason=getLastSeason, episodeNumber=1).first()
        return getLastSeason.release.year

    def getPosterSmall(self):
        getSeason = TelevisionSeason.objects.filter(televisionSeries=self).first()
        return getSeason.posterSmall.url

    class Meta:
        verbose_name = "Television"
        verbose_name_plural = "Television"


class TelevisionSeason(models.Model):
    title = models.CharField(max_length=500, null=True, blank=True, editable=True)
    televisionSeries = models.ForeignKey(Television, on_delete=models.CASCADE, default=1)
    release = models.DateField(default=timezone.now, null=True, blank=True)
    synopsis = models.CharField(max_length=500, null=True, blank=True)
    seasonNumber = models.IntegerField(default=1)
    episodeCount = models.IntegerField(default=1)
    trailerVideoPath = models.CharField(max_length=500, null=True, blank=True)
    poster = models.ImageField(default='', upload_to='televisionPosters', null=True, blank=True)
    posterSmall = models.ImageField(default='', upload_to='televisionPosters', null=True, blank=True)
    cover = models.ImageField(default='', upload_to='televisionCoverImages', null=True, blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)
    tmdbid = models.CharField(max_length=20,null=True,blank=True,editable=True)

    #Overwritten save method to populate the slugfield based on the television series' title and release date
    def save(self, *args, **kwargs):
        super().save()
        if not self.slug:
            self.slug = slugify(self.televisionSeries.title + "-" + str(self.televisionSeries.tmdbid)) + "-season-" + str(self.seasonNumber)
        super(TelevisionSeason, self).save(*args, **kwargs)

    def __str__(self):
        if self.title is None or self.title == "":
            return (str(self.televisionSeries.title) + " - S" + str(self.seasonNumber))
        else:
            return (str(self.televisionSeries.title) + " - " + self.title)
    class Meta:
        verbose_name = "Television - Season"
        verbose_name_plural = "Television - Seasons"


class TelevisionEpisode(models.Model):
    title = models.CharField(max_length=500, default='NoTelevisionEpisodeTitleSpecified')
    televisionSeason = models.ForeignKey(TelevisionSeason, on_delete=models.CASCADE, default=1)
    episodeNumber = models.IntegerField(default=1)
    release = models.DateField(default=timezone.now)
    synopsis = models.CharField(max_length=500, default='', blank=True)
    trailerVideoPath = models.CharField(max_length=500, default='', blank=True)
    stillImage = models.ImageField(default='', upload_to='televisionStills', null=True, blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)
    tmdbid = models.CharField(max_length=20,null=True,blank=True,editable=True)

    #Overwritten save method to populate the slugfield based on the television series' title and release date
    def save(self, *args, **kwargs):
        super().save()
        if not self.slug:
            self.slug = slugify(str(self.televisionSeason.televisionSeries.tmdbid) + "-" + self.televisionSeason.televisionSeries.title) + "-s" + str(self.televisionSeason.seasonNumber) + "-e" + str(self.episodeNumber)
        super(TelevisionEpisode, self).save(*args, **kwargs)

    def __str__(self):
        return self.televisionSeason.televisionSeries.title + " - S" + str(self.televisionSeason.seasonNumber) + " - E" + str(self.episodeNumber)

    #Gets the start year of the television series
    def getYear(self):
        return self.release.year

    #Gets the end year of the television series
    def getEndYear(self):
        return self.end.year

    class Meta:
        verbose_name = "Television - Episode"
        verbose_name_plural = "Television - Episodes"

class VideoGame(models.Model):
    title = models.CharField(max_length=500, default='NoVideoGameTitleSpecified')
    release = models.DateField(default=timezone.now)
    synopsis = models.CharField(max_length=1000, default='', blank=True)
    trailerVideoPath = models.CharField(max_length=500, default='', blank=True)
    poster = models.ImageField(default='', upload_to='posters', blank=True)
    cover = models.ImageField(default='', upload_to='coverImages', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    #Overwritten save method to populate the slugfield based on the game's title and release date
    def save(self, *args, **kwargs):
        super().save()
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(self.release))
            super(VideoGame, self).save(*args, **kwargs)

    def __str__(self):
        return (self.title + " - " + str(self.release.year))

    #Gets the release year of the video game
    def getYear(self):
        return self.release.year

    class Meta:
        verbose_name = "Video Game"
        verbose_name_plural = "Video Games"

class Book(models.Model):
    title = models.CharField(max_length=500, default='NoBookTitleSpecified')
    release = models.CharField(max_length=10, default='2000')
    synopsis = models.CharField(max_length=500, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    pages = models.IntegerField(default=100, blank=True)
    image = models.ImageField(default='', upload_to='bookImages', blank=True)
    cover = models.ImageField(default='', upload_to='bookCoverImages', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    #Overwritten save method to populate the slugfield based on the book's title and release date
    def save(self, *args, **kwargs):
        super().save()
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(self.release))
            super(Book, self).save(*args, **kwargs)

    def __str__(self):
        return self.title + " - " + self.release

    class Meta:
        verbose_name = "Books"
        verbose_name_plural = "Books"

class WebSeries(models.Model):
    title = models.CharField(max_length=500, default='NoWebSeriesTitleSpecified')
    ongoing = models.BooleanField(default=False)
    release = models.DateField(default=timezone.now)
    end = models.DateField(default=timezone.now)
    seasons = models.IntegerField(default=1)
    episodes = models.IntegerField(default=1)
    synopsis = models.CharField(max_length=500, default='', blank=True)
    trailerVideoPath = models.CharField(max_length=500, default='', blank=True)
    poster = models.ImageField(default='', upload_to='posters', blank=True)
    cover = models.ImageField(default='', upload_to='coverImages', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    #Overwritten save method to populate the slugfield based on the web series' title and release date
    def save(self, *args, **kwargs):
        super().save()
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(self.release))
        super(WebSeries, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    #Gets the web series' start year
    def getYear(self):
        return self.release.year

    #Gets the web series' end year
    def getEndYear(self):
        return self.end.year

    class Meta:
        verbose_name = "Web Series"
        verbose_name_plural = "Web Series"

#---Genres and Genre Mappings------------------------------------------------------------------------------------------#
class Genre(models.Model):
    title = models.CharField(max_length=500, default='NoGenreSpecified')
    image = models.ImageField(blank=True, default='', upload_to='icons')
    slug = models.SlugField(max_length=150, blank=True, editable=True, default='')

    def __str__(self):
        return self.title

    #Overwritten save method to populate the slugfield based on the genre name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Genre, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Genre - Standard"
        verbose_name_plural = "Genres - Standard"

class VideoGameGenre(models.Model):
    title = models.CharField(max_length=500, default='NoVideoGameGenreSpecified')
    image = models.ImageField(blank=True, default='', upload_to='icons')
    slug = models.SlugField(max_length=150, blank=True, editable=True, default='')

    def __str__(self):
        return self.title

    #Overwritten save method to populate the slugfield based on the genre name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(VideoGameGenre, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Genre - Video Game"
        verbose_name_plural = "Genres - Video Games"

class BookGenre(models.Model):
    title = models.CharField(max_length=500, default='NoBookSpecified')
    image = models.ImageField(blank=True, default='', upload_to='icons')
    slug = models.SlugField(max_length=150, blank=True, editable=True, default='')

    def __str__(self):
        return self.title

    #Overwritten save method to populate the slugfield based on the genre name
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(BookGenre, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Genre - Book"
        verbose_name_plural = "Genres - Books"

class FilmGenreMapping(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return (self.film.title + " | " + self.genre.title)

    class Meta:
        verbose_name = "Films - Genre Mapping"
        verbose_name_plural = "Films - Genre Mappings"

class TelevisionGenreMapping(models.Model):
    television = models.ForeignKey(Television, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return (self.television.title + " | " + self.genre.title)

    class Meta:
        verbose_name = "Television - Genre Mapping"
        verbose_name_plural = "Television - Genre Mappings"

class VideoGameGenreMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    genre = models.ForeignKey(VideoGameGenre, on_delete=models.CASCADE)

    def __str__(self):
        return (self.videoGame.title + " | " + self.genre.title)

    class Meta:
        verbose_name = "Video Games - Genre Mapping"
        verbose_name_plural = "Video Games - Genre Mappings"

class BookGenreMapping(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    genre = models.ForeignKey(BookGenre, on_delete=models.CASCADE)

    def __str__(self):
        return (self.book.title + " | " + self.genre.title)

    class Meta:
        verbose_name = "Books - Genre Mapping"
        verbose_name_plural = "Books - Genre Mappings"


class WebSeriesGenreMapping(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return (self.webSeries.title + " | " + self.genre.title)

    class Meta:
        verbose_name = "Web Series - Genre Mapping"
        verbose_name_plural = "Web Series - Genre Mappings"

#---Company Mappings---------------------------------------------------------------------------------------------------#
class FilmCompanyMapping(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.ForeignKey(CompanyRole, on_delete=models.CASCADE)

    def __str__(self):
        return (self.company.name + " || " + self.film.title + " || " + self.role.companyRoleName)

    class Meta:
        verbose_name = "Films - Company Mapping"
        verbose_name_plural = "Films - Company Mappings"

class TelevisionCompanyMapping(models.Model):
    television = models.ForeignKey(Television, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.ForeignKey(CompanyRole, on_delete=models.CASCADE)

    def __str__(self):
        return (self.company.name + " || " + self.television.title + " || " + self.role.companyRoleName)

    class Meta:
        verbose_name = "Television - Company Mapping"
        verbose_name_plural = "Television - Company Mappings"

class VideoGameCompanyMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.ForeignKey(CompanyRole, on_delete=models.CASCADE)

    def __str__(self):
        return (self.company.name + " || " + self.videoGame.title + " || " + self.role.companyRoleName)

    class Meta:
        verbose_name = "Video Game - Company Mapping"
        verbose_name_plural = "Video Games - Company Mappings"

class BookCompanyMapping(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.ForeignKey(CompanyRole, on_delete=models.CASCADE)

    def __str__(self):
        return (self.company.name + " || " + self.book.title + " || " + self.role.companyRoleName)

    class Meta:
        verbose_name = "Book - Company Mapping"
        verbose_name_plural = "Books - Company Mappings"

class WebSeriesCompanyMapping(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.ForeignKey(CompanyRole, on_delete=models.CASCADE)

    def __str__(self):
        return (self.company.name + " || " + self.webSeries.title + " || " + self.role.companyRoleName)

    class Meta:
        verbose_name = "Web Series - Company Mapping"
        verbose_name_plural = "Web Series - Company Mappings"

#---Media-Person Mappings----------------------------------------------------------------------------------------------#
class FilmPersonMapping(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    role = models.ForeignKey(PersonRole, on_delete=models.CASCADE, default=1)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True)
    character = models.CharField(max_length=500, default='', blank=True)
    billing = models.IntegerField(default=1, unique=False)

    def __str__(self):
        return (self.person.name + " || " + self.film.title + " || " + self.role.role)

    def getPerson(self):
        return (self.person.name)

    class Meta:
        verbose_name = "Films - Person Mapping"
        verbose_name_plural = "Films - Person Mappings"

class TelevisionPersonMapping(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    television = models.ForeignKey(Television, on_delete=models.CASCADE)
    role = models.ForeignKey(PersonRole, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, default=1)
    episodes = models.IntegerField(default=1, blank=True, null=True)
    character = models.CharField(max_length=500, default='', blank=True)
    billing = models.IntegerField(default=1, unique=False)

    def __str__(self):
        return (self.person.getFullName + " - " + self.television.title + " - " + self.role.role)

    def getPerson(self):
        return (self.person.firstName + " " + self.person.surname)

    class Meta:
        verbose_name = "Television - Person Mapping"
        verbose_name_plural = "Television - Person Mappings"

class TelevisionEpisodePersonMapping(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    televisionEpisode = models.ForeignKey(TelevisionEpisode, on_delete=models.CASCADE)
    role = models.ForeignKey(PersonRole, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, default=1)
    episodes = models.IntegerField
    character = models.CharField(max_length=500, default='', blank=True)
    billing = models.IntegerField(default=1, unique=False)
    guestCast = models.BooleanField(default=False,blank=True)

    def __str__(self):
        return (self.person.getFullName()
                + " - "
                + self.televisionEpisode.televisionSeason.televisionSeries.title
                + " - S"
                + str(self.televisionEpisode.televisionSeason.seasonNumber)
                + "E"
                + str(self.televisionEpisode.episodeNumber)
                + " - "
                + self.role.role)

    def getPerson(self):
        return (self.person.getFullName())

    class Meta:
        verbose_name = "Television Episode - Person Mapping"
        verbose_name_plural = "Television Episode - Person Mappings"


class VideoGamePersonMapping(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    videogame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    role = models.ForeignKey(PersonRole, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, default=1)
    character = models.CharField(max_length=500, default='', blank=True)
    billing = models.IntegerField(default=1, unique=False)

    def __str__(self):
        return (self.person.firstName + " " + self.person.surname + " || " + self.videogame.title + " || " + self.role.role)

    def getPerson(self):
        return (self.person.firstName + " " + self.person.surname)

    class Meta:
        verbose_name = "Video Games - Person Mapping"
        verbose_name_plural = "Video Games - Person Mappings"

class BookPersonMapping(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    role = models.ForeignKey(PersonRole, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, default=1)

    def __str__(self):
        return (self.person.firstName + " " + self.person.surname + " || " + self.book.title + " || " + self.role.role)

    def getPerson(self):
        return (self.person.firstName + " " + self.person.surname)

    class Meta:
        verbose_name = "Book - Person Mapping"
        verbose_name_plural = "Books - Person Mappings"

class WebSeriesPersonMapping(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    webSeries = models.ForeignKey(WebSeries, on_delete=models.CASCADE)
    role = models.ForeignKey(PersonRole, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, blank=True, default=1)
    character = models.CharField(max_length=500, default='', blank=True)
    billing = models.IntegerField(default=1, unique=False)

    def __str__(self):
        return (self.person.firstName + " " + self.person.surname + " || " + self.webSeries.title + " || " + self.role.role)

    def getPerson(self):
        return (self.person.firstName + " " + self.person.surname)

    class Meta:
        verbose_name = "Web Series - Person Mapping"
        verbose_name_plural = "Web Series - Person Mappings"

#---Franchises and Media-FranchiseSubcategory Mappings-----------------------------------------------------------------#
class Franchise(models.Model):
    title = models.CharField(max_length=500, default='NoFranchiseNameSpecified')
    image = models.ImageField(blank=True, upload_to='franchises')
    description = models.CharField(max_length=1000, blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)
    showPeople = models.BooleanField(default=False)
    showProducers = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Franchise, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Franchise"
        verbose_name_plural = "Franchises"

class FranchiseSubcategory(models.Model):
    parentFranchise = models.ForeignKey(Franchise, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, default='NoFranchiseSubCategoryNameSpecified')
    subCategoryOrder = models.IntegerField(default=1)

    def __str__(self):
        return self.parentFranchise.title + " - " + self.title

    class Meta:
        verbose_name = "Franchise - Subcategory"
        verbose_name_plural = "Franchises - Subcategories"

class VideoGameFranchise(models.Model):
    title = models.CharField(max_length=500, default='NoFranchiseNameSpecified')
    image = models.ImageField(blank=True, upload_to='franchises')
    description = models.CharField(max_length=1000, blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(VideoGameFranchise, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Video Game Franchise"
        verbose_name_plural = "Video Game Franchises"

class VideoGameFranchiseSubcategory(models.Model):
    parentFranchise = models.ForeignKey(VideoGameFranchise, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, default='NoVideoGameFranchiseSubCategoryNameSpecified')
    subCategoryOrder = models.IntegerField(default=1)

    def __str__(self):
        return self.parentFranchise.title + " - " + self.title

    class Meta:
        verbose_name = "Video Game Franchise Subcategory"
        verbose_name_plural = "Video Game Franchise Subcategories"

class FilmFranchiseSubcategoryMapping(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    franchiseSubcategory = models.ForeignKey(FranchiseSubcategory, on_delete=models.CASCADE)
    orderInFranchise = models.IntegerField(default=1)

    def __str__(self):
        return (self.franchiseSubcategory.title + " - " + self.film.title)

    class Meta:
        verbose_name = "Films - Franchise  Subcategory Mapping"
        verbose_name_plural = "Films - Franchise  Subcategory Mappings"

class TelevisionFranchiseSubcategoryMapping(models.Model):
    television = models.ForeignKey(Television, on_delete=models.CASCADE)
    franchiseSubcategory = models.ForeignKey(FranchiseSubcategory, on_delete=models.CASCADE)
    orderInFranchise = models.IntegerField(default=1)

    def __str__(self):
        return (self.franchiseSubcategory.title + " - " + str(self.orderInFranchise) + " - " + self.television.title)

    class Meta:
        verbose_name = "Television - Franchise  Subcategory Mapping"
        verbose_name_plural = "Television - Franchise  Subcategory Mappings"

class VideoGameFranchiseSubcategoryMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    franchiseSubcategory = models.ForeignKey(FranchiseSubcategory, on_delete=models.CASCADE)
    orderInFranchise = models.IntegerField(default=1)

    def __str__(self):
        return (self.franchiseSubcategory.title + " - " + str(self.orderInFranchise) + " - " + self.videoGame.title)

    class Meta:
        verbose_name = "Video Games - Franchise  Subcategory Mapping"
        verbose_name_plural = "Video Games - Franchise  Subcategory Mappings"

class VideoGameVideoGameFranchiseSubcategoryMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    videoGameFranchiseSubcategory = models.ForeignKey(VideoGameFranchiseSubcategory, on_delete=models.CASCADE)
    orderInFranchise = models.IntegerField(default=1)

    def __str__(self):
        return (self.videoGameFranchiseSubcategory.title + " - " + str(self.orderInFranchise) + " - " + self.videoGame.title)

    class Meta:
        verbose_name = "Video Games - Video Game Franchise  Subcategory Mapping"
        verbose_name_plural = "Video Games - Video Game Franchise  Subcategory Mappings"

class BookFranchiseSubcategoryMapping(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    franchiseSubcategory = models.ForeignKey(FranchiseSubcategory, on_delete=models.CASCADE)
    orderInFranchise = models.IntegerField(default=1)

    def __str__(self):
        return (self.franchiseSubcategory.title + " - " + str(self.orderInFranchise) + " - " + self.book.title)

    class Meta:
        verbose_name = "Books - Franchise  Subcategory Mapping"
        verbose_name_plural = "Books - Franchise  Subcategory Mappings"

class WebSeriesFranchiseSubcategoryMapping(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.CASCADE)
    franchiseSubcategory = models.ForeignKey(FranchiseSubcategory, on_delete=models.CASCADE)
    orderInFranchise = models.IntegerField(default=1)

    def __str__(self):
        return (self.franchiseSubcategory.title + " - " + str(self.orderInFranchise) + " - " + self.webSeries.title)

    class Meta:
        verbose_name = "Web Series - Franchise  Subcategory Mapping"
        verbose_name_plural = "Web Series - Franchise  Subcategory Mappings"

#---Franchise-Genre Mappings-------------------------------------------------------------------------------------------#
class FranchiseGenreMapping(models.Model):
    franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    def __str__(self):
        return (self.franchise.title + " - " + self.genre.title)

    class Meta:
        verbose_name = "Franchises - Genre Mapping"
        verbose_name_plural = "Franchises - Genre Mappings"

class VideoGameFranchiseGenreMapping(models.Model):
    franchise = models.ForeignKey(VideoGameFranchise, on_delete=models.CASCADE)
    genre = models.ForeignKey(VideoGameGenre, on_delete=models.CASCADE)

    def __str__(self):
        return (self.franchise.title + " - " + self.genre.title)

    class Meta:
        verbose_name = "Video Game Franchises - Genre Mapping"
        verbose_name_plural = "Video Game Franchises - Genre Mappings"

#---Company-Franchise Mappings-----------------------------------------------------------------------------------------#
class FranchiseCompanyMapping(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default='')
    franchise = models.ForeignKey(Franchise, on_delete=models.CASCADE, default='')

    def __str__(self):
        return (self.company.name + " - " + self.franchise.title)

    class Meta:
        verbose_name = "Company - Franchise Mapping"
        verbose_name_plural = "Companies - Franchise Mappings"

class VideoGameFranchiseCompanyMapping(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, default='')
    franchise = models.ForeignKey(VideoGameFranchise, on_delete=models.CASCADE, default='')

    def __str__(self):
        return (self.company.name + " - " + self.franchise.title)

    class Meta:
        verbose_name = "Company - Video Game Franchise Mapping"
        verbose_name_plural = "Companies - Video Game Franchise Mappings"

#---Video Game Consoles and Mappings-----------------------------------------------------------------------------------#
class Console(models.Model):
    name = models.CharField(max_length=500, default='NoConsoleNameSpecified')
    shortName = models.CharField(max_length=500, default='NoShortConsoleNameSpecified')
    release = models.DateField(default=timezone.now)
    developer = models.ForeignKey(Company, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=150, blank=True, editable=True, default='')
    image = models.ImageField(blank=True, upload_to='consoles')

    #Overwritten save method to populate the slugfield based on the console's name
    def save(self, *args, **kwargs):
        super().save()
        if not self.slug:
            self.slug = slugify(self.shortName)
        super(Console, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Video Game Console"
        verbose_name_plural = "Video Game Consoles"

class ConsoleVersion(models.Model):
    name = models.CharField(max_length=500, default='NoConsoleNameSpecified')
    shortName = models.CharField(max_length=500, default='None')
    console = models.ForeignKey(Console, on_delete=models.CASCADE)
    release = models.DateField(default=timezone.now)
    image = models.ImageField(blank=True, upload_to='consoles')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Video Game Console - Version"
        verbose_name_plural = "Video Game Consoles - Versions"

class VideoGameConsoleMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    console = models.ForeignKey(Console, on_delete=models.CASCADE)
    featured = models.BooleanField(default=False)

    def __str__(self):
        return (self.videoGame.title + " | " + self.console.name)

    class Meta:
        verbose_name = "Video Games - Console Mapping"
        verbose_name_plural = "Video Games - Console Mappings"

#---Awards-------------------------------------------------------------------------------------------------------------#
class AwardType(models.Model):
    name = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Awards - Type"
        verbose_name_plural = "Awards - Types"

class AwardsShow(models.Model):
    name = models.CharField(max_length=50, default='')
    award = models.ForeignKey(AwardType, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name + " | " + str(self.date)

    class Meta:
        verbose_name = "Awards - Show"
        verbose_name_plural = "Awards - Shows"

class AwardsCategories(models.Model):
    name = models.CharField(max_length=50)
    awardType = models.ForeignKey(AwardType, on_delete=models.CASCADE)
    categoryOrder = models.IntegerField(default=1)
    personCompanyPriority = models.BooleanField(default=False)

    def __str__(self):
        return (self.name + " | " + self.awardType.name)

    class Meta:
        verbose_name = "Awards - Category"
        verbose_name_plural = "Awards - Categories"

#---Media Awards Mappings----------------------------------------------------------------------------------------------#
class FilmAwardMapping(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.CASCADE, default='')
    category = models.ForeignKey(AwardsCategories, on_delete=models.CASCADE, null=True)
    win = models.BooleanField(default=False)

    def __str__(self):
        return (self.film.title + " | " + self.awardsShow.name + " | " + self.category.name)

    class Meta:
        verbose_name = "Film - Award"
        verbose_name_plural = "Films - Awards"

class TelevisionAwardMapping(models.Model):
    television = models.ForeignKey(Television, on_delete=models.CASCADE)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.CASCADE, default='')
    category = models.ForeignKey(AwardsCategories, on_delete=models.CASCADE, null=True)
    win = models.BooleanField(default=False)

    def __str__(self):
        return (self.television.title + " | " + self.awardsShow.name + " | " + self.category.name)

    class Meta:
        verbose_name = "Television - Award"
        verbose_name_plural = "Television - Awards"

class VideoGameAwardMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.CASCADE, default='')
    category = models.ForeignKey(AwardsCategories, on_delete=models.CASCADE, null=True)
    win = models.BooleanField(default=False)

    def __str__(self):
        return (self.videoGame.title + " | " + self.awardsShow.name + " | " + self.category.name)

    class Meta:
        verbose_name = "Video Game - Award"
        verbose_name_plural = "Video Games - Awards"

class BookAwardMapping(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.CASCADE, default='')
    category = models.ForeignKey(AwardsCategories, on_delete=models.CASCADE, null=True)
    win = models.BooleanField(default=False)

    def __str__(self):
        return (self.book.title + " | " + self.awardsShow.name + " | " + self.category.name)

    class Meta:
        verbose_name = "Book - Award"
        verbose_name_plural = "Books - Awards"

class WebSeriesAwardMapping(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.CASCADE)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.CASCADE, default='')
    category = models.ForeignKey(AwardsCategories, on_delete=models.CASCADE, null=True)
    win = models.BooleanField(default=False)

    def __str__(self):
        return (self.webSeries.title + " | " + self.awardsShow.name + " | " + self.category.name)

    class Meta:
        verbose_name = "Web Series - Award"
        verbose_name_plural = "Web Series - Awards"

# ---Award Credit Mappings---------------------------------------------------------------------------------------------#
class FilmAwardCreditMapping(models.Model):
    FilmAwardMapping = models.ForeignKey(FilmAwardMapping, on_delete=models.CASCADE, default='')
    Person = models.ForeignKey(Person, on_delete=models.CASCADE, blank=True, null=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        if self.Person:
            return (self.FilmAwardMapping.film.title
                    + " | " + self.FilmAwardMapping.awardsShow.name
                    + " | " + self.Person.getFullName())
        if self.Company:
            return (self.FilmAwardMapping.film.title
                    + " | " + self.FilmAwardMapping.awardsShow.name
                    + " | " + self.Company.name)


    class Meta:
        verbose_name = "Film - Award Credit Mapping"
        verbose_name_plural = "Films - Award Credit Mappings"

class TelevisionAwardCreditMapping(models.Model):
    TelevisionAwardMapping = models.ForeignKey(TelevisionAwardMapping, on_delete=models.CASCADE, default='')
    Person = models.ForeignKey(Person, on_delete=models.CASCADE, default='', blank=True, null=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, default='', blank=True, null=True)

    def __str__(self):
        return (self.TelevisionAwardMapping.television.title + " | " + self.TelevisionAwardMapping.awardsShow.name)

    class Meta:
        verbose_name = "Television - Award Credit Mapping"
        verbose_name_plural = "Television - Award Credit Mappings"

class VideoGameAwardCreditMapping(models.Model):
    VideoGameAwardMapping = models.ForeignKey(VideoGameAwardMapping, on_delete=models.CASCADE, default='')
    Person = models.ForeignKey(Person, on_delete=models.CASCADE, default='', blank=True, null=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, default='', blank=True, null=True)

    def __str__(self):
        return (self.VideoGameAwardMapping.videoGame.title + " | " + self.VideoGameAwardMapping.awardsShow.name)

    class Meta:
        verbose_name = "Video Game - Award Credit Mapping"
        verbose_name_plural = "Video Games - Award Credit Mappings"

class BookAwardCreditMapping(models.Model):
    BookAwardMapping = models.ForeignKey(BookAwardMapping, on_delete=models.CASCADE, default='')
    Person = models.ForeignKey(Person, on_delete=models.CASCADE, default='', blank=True, null=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, default='', blank=True, null=True)

    def __str__(self):
        return (self.BookAwardMapping.book.title + " | " + self.BookAwardMapping.awardsShow.name)

    class Meta:
        verbose_name = "Book - Award Credit Mapping"
        verbose_name_plural = "Books - Award Credit Mappings"

class WebSeriesAwardCreditMapping(models.Model):
    WebSeriesAwardMapping = models.ForeignKey(WebSeriesAwardMapping, on_delete=models.CASCADE, default='')
    Person = models.ForeignKey(Person, on_delete=models.CASCADE, default='', blank=True, null=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, default='', blank=True, null=True)

    def __str__(self):
        return (self.WebSeriesAwardMapping.webSeries.title + " | " + self.WebSeriesAwardMapping.awardsShow.name)

    class Meta:
        verbose_name = "Web Series - Award Credit Mapping"
        verbose_name_plural = "Web Series - Award Credit Mappings"

# ---Additional Image Mappings-----------------------------------------------------------------------------------------#
class MiscImages(models.Model):
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.CASCADE, null=True)
    image = models.ImageField(default='MissingIcon.png', upload_to='miscImages', blank=True)

    def __str__(self):
        return (self.awardsShow.name + " | " + str(self.id))

    class Meta:
        verbose_name = "Misc - Additional Image"
        verbose_name_plural = "Misc - Additional Images"

class PersonImages(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(default='MissingIcon.png', upload_to='people', blank=True)

    def __str__(self):
        return (self.person.getFullName() + " | " + str(self.id))

    class Meta:
        verbose_name = "Person - Additional Image"
        verbose_name_plural = "People - Additional Images"

class FilmImages(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    image = models.ImageField(default='MissingIcon.png', upload_to='extraImages', blank=True)

    def __str__(self):
        return (self.film.title + " | " + str(self.image))

    class Meta:
        verbose_name = "Film - Additional Image"
        verbose_name_plural = "Films - Additional Images"

class TelevisionImages(models.Model):
    television = models.ForeignKey(Television, on_delete=models.CASCADE)
    image = models.ImageField(default='MissingIcon.png', upload_to='extraImages', blank=True)

    def __str__(self):
        return (self.television.title + " | " + str(self.id))

    class Meta:
        verbose_name = "Television - Additional Image"
        verbose_name_plural = "Television - Additional Images"

class VideoGameImages(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    image = models.ImageField(default='MissingIcon.png', upload_to='extraImages', blank=True)

    def __str__(self):
        return (self.videoGame.title + " | " + str(self.id))

    class Meta:
        verbose_name = "Video Game - Additional Image"
        verbose_name_plural = "Video Games - Additional Images"

class BookImages(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    image = models.ImageField(default='MissingIcon.png', upload_to='extraImages', blank=True)

    def __str__(self):
        return (self.book.title + " | " + str(self.id))

    class Meta:
        verbose_name = "Book - Additional Image"
        verbose_name_plural = "Books - Additional Images"

class WebSeriesImages(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.CASCADE)
    image = models.ImageField(default='MissingIcon.png', upload_to='extraImages', blank=True)

    def __str__(self):
        return (self.webSeries.title + " | " + str(self.id))

    class Meta:
        verbose_name = "Web Series - Additional Image"
        verbose_name_plural = "Web Series - Additional Images"

# ---Media Tags and Mappings-------------------------------------------------------------------------------------------#
class Tag(models.Model):
    name = models.CharField(max_length=50, default='', primary_key=True)

    #Overwritten save method to populate the slugfield based on the tag's name
    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)

    def __str__(self):
        return (self.name)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

class FilmTagMapping(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return (self.tag.name + " - " + self.film.title)

    class Meta:
        verbose_name = "Film - Tag Mapping"
        verbose_name_plural = "Films - Tag Mappings"

class TelevisionTagMapping(models.Model):
    television = models.ForeignKey(Television, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return (self.tag.name + " - " + self.television.title)

    class Meta:
        verbose_name = "Television - Tag Mapping"
        verbose_name_plural = "Television - Tag Mappings"

class VideoGameTagMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return (self.tag.name + " - " + self.videoGame.title)

    class Meta:
        verbose_name = "Video Game - Tag Mapping"
        verbose_name_plural = "Video Game - Tag Mappings"

class BookTagMapping(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return (self.tag.name + " - " + self.book.title)

    class Meta:
        verbose_name = "Book - Tag Mapping"
        verbose_name_plural = "Book - Tag Mappings"

class WebSeriesTagMapping(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return (self.tag.name + " - " + self.webSeries.title)

    class Meta:
        verbose_name = "Web Series - Tag Mapping"
        verbose_name_plural = "Web Series - Tag Mappings"

#-- Highest Rating Stores ---------------------------------------------------------------------------------------------#
class HighestRatedFilms(models.Model):
    media = models.ForeignKey(Film, on_delete=models.CASCADE)
    rating = models.FloatField(default=1.0)
    rank = models.IntegerField(default=1)

    def __str__(self):
        return (self.media.title + " - " + str(self.rank))

    class Meta:
        verbose_name = "Highest Rated Film"
        verbose_name_plural = "Highest Rated Films"

class HighestRatedTelevision(models.Model):
    media = models.ForeignKey(Television, on_delete=models.CASCADE)
    rating = models.FloatField(default=1.0)
    rank = models.IntegerField(default=1)

    def __str__(self):
        return (self.media.title + " - " + str(self.rank))

    class Meta:
        verbose_name = "Highest Rated Television"
        verbose_name_plural = "Highest Rated Television"

class HighestRatedVideoGames(models.Model):
    media = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    rating = models.FloatField(default=1.0)
    rank = models.IntegerField(default=1)

    def __str__(self):
        return (self.media.title + " - " + str(self.rank))

    class Meta:
        verbose_name = "Highest Rated Video Game"
        verbose_name_plural = "Highest Rated Video Games"

class HighestRatedBooks(models.Model):
    media = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.FloatField(default=1.0)
    rank = models.IntegerField(default=1)

    def __str__(self):
        return (self.media.title + " - " + str(self.rank))

    class Meta:
        verbose_name = "Highest Rated Book"
        verbose_name_plural = "Highest Rated Books"

class HighestRatedWebSeries(models.Model):
    media = models.ForeignKey(WebSeries, on_delete=models.CASCADE)
    rating = models.FloatField(default=1.0)
    rank = models.IntegerField(default=1)

    def __str__(self):
        return (self.media.title + " - " + str(self.rank))

    class Meta:
        verbose_name = "Highest Rated Web Series"
        verbose_name_plural = "Highest Rated Web Series"