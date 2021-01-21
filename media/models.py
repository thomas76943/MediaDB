from PIL import Image
from django.db import models
from django.utils import timezone
from django.contrib.staticfiles.urls import static

#---People and Roles---------------------------------------------------------------------------------------------------#
from django.utils.text import slugify

class Person(models.Model):
    firstName = models.CharField(max_length=500, default='NoFirstNameSpecified')
    surname = models.CharField(max_length=500, blank=True, default='NoSurnameSpecified')
    DoB = models.DateField(default=timezone.now)
    alive = models.BooleanField(default=True)
    DoD = models.DateField(blank=True, null=True)
    imageFilePath = models.CharField(max_length=500, default='../static/media/MissingIcon.png')
    bio = models.CharField(max_length=1000, default='', blank=True)
    image = models.ImageField(default='MissingIcon.png', upload_to='people', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    def __str__(self):
        return (self.firstName + " " + self.surname)

    def getFullName(self):
        return (self.firstName + " " + self.surname)

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.image.path)
        if img.height > 600 or img.width > 600:
            output_size = (600,600)
            img.thumbnail(output_size)
            img.save(self.image.path)
        if not self.slug:
            self.slug = slugify(self.getFullName() + "-" + str(self.DoB))
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

#---Companies----------------------------------------------------------------------------------------------------------#
class Company(models.Model):
    name = models.CharField(max_length=500, default='NoFilmStudioNameSpecified')
    baseCountry = models.CharField(max_length=500, default='NoCountrySpecified')
    dateFounded = models.DateField(default=timezone.now)
    image = models.ImageField(upload_to='companyLogos', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.image.path)
        if img.height > 600 or img.width > 600:
            output_size = (600,600)
            img.thumbnail(output_size)
            img.save(self.image.path)
        if not self.slug:
            self.slug = slugify(self.name)
        super(Company, self).save(*args, **kwargs)


class CompanyRole(models.Model):
    companyRoleName = models.CharField(max_length=500, default='NoCompanyRoleNameSpecified')

    def __str__(self):
        return self.companyRoleName

    class Meta:
        verbose_name = "Company - Role Type"
        verbose_name_plural = "Companies - Role Types"

#---Media Types--------------------------------------------------------------------------------------------------------#
class Film(models.Model):
    title = models.CharField(max_length=500, default='NoFilmTitleSpecified')
    release = models.DateField(default=timezone.now)
    rating = models.CharField(max_length=10, blank=True)
    synopsis = models.CharField(max_length=500, default='', blank=True)
    length = models.IntegerField(null=True, blank=True)
    budget = models.IntegerField(null=True, blank=True)
    boxOffice = models.IntegerField(null=True, blank=True)
    trailerVideoPath = models.CharField(max_length=500, default='', blank=True)
    poster = models.ImageField(default='MissingIcon.png', upload_to='posters', blank=True)
    cover = models.ImageField(default='', upload_to='coverImages', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    def save(self, *args, **kwargs):
        super().save()
        if self.poster:
            img = Image.open(self.poster.path)
            if img.height > 600 or img.width > 600:
                output_size = (600,600)
                img.thumbnail(output_size)
                img.save(self.poster.path)
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(self.release))
        super(Film, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def getYear(self):
        return self.release.year

    def get_absolute_url(self):
        return ''

    class Meta:
        verbose_name = "Film"
        verbose_name_plural = "Films"

class Television(models.Model):
    title = models.CharField(max_length=500, default='NoTelevisionTitleSpecified')
    ongoing = models.BooleanField(default=False)
    release = models.DateField(default=timezone.now)
    end = models.DateField(default=timezone.now, blank=True)
    synopsis = models.CharField(max_length=500, default='', blank=True)
    seasons = models.IntegerField(default=1)
    episodes = models.IntegerField(default=1)
    posterFilePath = models.CharField(max_length=500, default='../static/media/MissingIcon.png')
    trailerVideoPath = models.CharField(max_length=500, default='', blank=True)
    coverImageFilePath = models.CharField(max_length=500, default='', blank=True)
    poster = models.ImageField(default='', upload_to='posters', blank=True)
    cover = models.ImageField(default='', upload_to='coverImages', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.poster.path)
        if img.height > 600 or img.width > 600:
            output_size = (600,600)
            img.thumbnail(output_size)
            img.save(self.poster.path)
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(self.release))
        super(Television, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def getYear(self):
        return self.release.year

    def getEndYear(self):
        return self.end.year

    class Meta:
        verbose_name = "Television"
        verbose_name_plural = "Television"

class VideoGame(models.Model):
    title = models.CharField(max_length=500, default='NoVideoGameTitleSpecified')
    release = models.DateField(default=timezone.now)
    synopsis = models.CharField(max_length=500, default='', blank=True)
    posterFilePath = models.CharField(max_length=500, default='../static/media/MissingIcon.png', blank=True)
    trailerVideoPath = models.CharField(max_length=500, default='', blank=True)
    coverImageFilePath = models.CharField(max_length=500, default='', blank=True)
    poster = models.ImageField(default='', upload_to='posters', blank=True)
    cover = models.ImageField(default='', upload_to='coverImages', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.poster.path)
        if img.height > 600 or img.width > 600:
            output_size = (600,600)
            img.thumbnail(output_size)
            img.save(self.poster.path)
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(self.release))
            super(VideoGame, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def getYear(self):
        return self.release.year

    class Meta:
        verbose_name = "Video Game"
        verbose_name_plural = "Video Games"

class Book(models.Model):
    title = models.CharField(max_length=500, default='NoBookTitleSpecified')
    release = models.DateField(default=timezone.now)
    synopsis = models.CharField(max_length=500, default='', blank=True)
    imageFilePath = models.CharField(max_length=500, default='../static/media/MissingIcon.png')
    coverImageFilePath = models.CharField(max_length=500, default='', blank=True)
    image = models.ImageField(default='', upload_to='bookImages', blank=True)
    cover = models.ImageField(default='', upload_to='bookCoverImages', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.image.path)
        if img.height > 600 or img.width > 600:
            output_size = (600, 600)
            img.thumbnail(output_size)
            img.save(self.image.path)
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(self.release))
            super(Book, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def getYear(self):
        return self.release.year

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
    posterFilePath = models.CharField(max_length=500, default='../static/media/MissingIcon.png')
    trailerVideoPath = models.CharField(max_length=500, default='', blank=True)
    coverImageFilePath = models.CharField(max_length=500, default='', blank=True)
    poster = models.ImageField(default='', upload_to='posters', blank=True)
    cover = models.ImageField(default='', upload_to='coverImages', blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.poster.path)
        if img.height > 600 or img.width > 600:
            output_size = (600,600)
            img.thumbnail(output_size)
            img.save(self.poster.path)
        if not self.slug:
            self.slug = slugify(self.title + "-" + str(self.release))
        super(WebSeries, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def getYear(self):
        return self.release.year

    def getEndYear(self):
        return self.end.year

    class Meta:
        verbose_name = "Web Series"
        verbose_name_plural = "Web Series"

#---Genre Mappings-------------------------------------------------------------------------------------------------------#
class Genre(models.Model):
    title = models.CharField(max_length=500, default='NoFilmGenreSpecified')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Genre - Standard"
        verbose_name_plural = "Genres - Standard"

class VideoGameGenre(models.Model):
    title = models.CharField(max_length=500, default='NoVideoGameGenreSpecified')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Genre - Video Game"
        verbose_name_plural = "Genres - Video Games"

class FilmGenreMapping(models.Model):
    film = models.ForeignKey(Film, on_delete=models.PROTECT)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT)

    def __str__(self):
        return (self.film.title + " | " + self.genre.title)

    class Meta:
        verbose_name = "Films - Genre Mapping"
        verbose_name_plural = "Films - Genre Mappings"

class TelevisionGenreMapping(models.Model):
    television = models.ForeignKey(Television, on_delete=models.PROTECT)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT)

    def __str__(self):
        return (self.television.title + " | " + self.genre.title)

    class Meta:
        verbose_name = "Television - Genre Mapping"
        verbose_name_plural = "Television - Genre Mappings"

class VideoGameGenreMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.PROTECT)
    genre = models.ForeignKey(VideoGameGenre, on_delete=models.PROTECT)

    def __str__(self):
        return (self.videoGame.title + " | " + self.genre.title)

    class Meta:
        verbose_name = "Video Games - Genre Mapping"
        verbose_name_plural = "Video Games - Genre Mappings"

class BookGenreMapping(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT)

    def __str__(self):
        return (self.book.title + " | " + self.genre.title)

    class Meta:
        verbose_name = "Books - Genre Mapping"
        verbose_name_plural = "Books - Genre Mappings"

class WebSeriesGenreMapping(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.PROTECT)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT)

    def __str__(self):
        return (self.webSeries.title + " | " + self.genre.title)

    class Meta:
        verbose_name = "Web Series - Genre Mapping"
        verbose_name_plural = "Web Series - Genre Mappings"

#---Company Mappings----------------------------------------------------------------------------------------------------#
class FilmCompanyMapping(models.Model):
    film = models.ForeignKey(Film, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    role = models.ForeignKey(CompanyRole, on_delete=models.PROTECT)

    def __str__(self):
        return (self.company.name + " || " + self.film.title + " || " + self.role.companyRoleName)

    class Meta:
        verbose_name = "Films - Company Mapping"
        verbose_name_plural = "Films - Company Mappings"

class TelevisionCompanyMapping(models.Model):
    television = models.ForeignKey(Television, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    role = models.ForeignKey(CompanyRole, on_delete=models.PROTECT)

    def __str__(self):
        return (self.company.name + " || " + self.television.title + " || " + self.role.companyRoleName)

    class Meta:
        verbose_name = "Television - Company Mapping"
        verbose_name_plural = "Television - Company Mappings"

class VideoGameCompanyMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    role = models.ForeignKey(CompanyRole, on_delete=models.PROTECT)

    def __str__(self):
        return (self.company.name + " || " + self.videoGame.title + " || " + self.role.companyRoleName)

    class Meta:
        verbose_name = "Video Game - Company Mapping"
        verbose_name_plural = "Video Games - Company Mappings"

class BookCompanyMapping(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    role = models.ForeignKey(CompanyRole, on_delete=models.PROTECT)

    def __str__(self):
        return (self.company.name + " || " + self.book.title + " || " + self.role.companyRoleName)

    class Meta:
        verbose_name = "Book - Company Mapping"
        verbose_name_plural = "Books - Company Mappings"

class WebSeriesCompanyMapping(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
    role = models.ForeignKey(CompanyRole, on_delete=models.PROTECT)

    def __str__(self):
        return (self.company.name + " || " + self.webSeries.title + " || " + self.role.companyRoleName)

    class Meta:
        verbose_name = "Web Series - Company Mapping"
        verbose_name_plural = "Web Series - Company Mappings"


#---Person Mappings----------------------------------------------------------------------------------------------------#
class FilmPersonMapping(models.Model):
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    film = models.ForeignKey(Film, on_delete=models.PROTECT)
    role = models.ForeignKey(PersonRole, on_delete=models.PROTECT)
    character = models.CharField(max_length=500, default='', blank=True)
    billing = models.IntegerField(default=1, unique=False)

    def __str__(self):
        return (self.person.firstName + " " + self.person.surname + " || " + self.film.title + " || " + self.role.role)

    def getPerson(self):
        return (self.person.firstName + " " + self.person.surname)

    class Meta:
        verbose_name = "Films - Person Mapping"
        verbose_name_plural = "Films - Person Mappings"

class TelevisionPersonMapping(models.Model):
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    television = models.ForeignKey(Television, on_delete=models.PROTECT)
    role = models.ForeignKey(PersonRole, on_delete=models.PROTECT)
    episodes = models.IntegerField
    character = models.CharField(max_length=500, default='', blank=True)
    billing = models.IntegerField(default=1, unique=False)

    def __str__(self):
        return (self.person.firstName + " " + self.person.surname + " || " + self.television.title + " || " + self.role.role)

    def getPerson(self):
        return (self.person.firstName + " " + self.person.surname)

    class Meta:
        verbose_name = "Television - Person Mapping"
        verbose_name_plural = "Television - Person Mappings"

class VideoGamePersonMapping(models.Model):
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    videogame = models.ForeignKey(VideoGame, on_delete=models.PROTECT)
    role = models.ForeignKey(PersonRole, on_delete=models.PROTECT)

    def __str__(self):
        return (self.person.firstName + " " + self.person.surname + " || " + self.videogame.title + " || " + self.role.role)

    def getPerson(self):
        return (self.person.firstName + " " + self.person.surname)

    class Meta:
        verbose_name = "Video Games - Person Mapping"
        verbose_name_plural = "Video Games - Person Mappings"

class BookPersonMapping(models.Model):
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    role = models.ForeignKey(PersonRole, on_delete=models.PROTECT)

    def __str__(self):
        return (self.person.firstName + " " + self.person.surname + " || " + self.book.title + " || " + self.role.role)

    def getPerson(self):
        return (self.person.firstName + " " + self.person.surname)

    class Meta:
        verbose_name = "Book - Person Mapping"
        verbose_name_plural = "Books - Person Mappings"

class WebSeriesPersonMapping(models.Model):
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    webSeries = models.ForeignKey(WebSeries, on_delete=models.PROTECT)
    role = models.ForeignKey(PersonRole, on_delete=models.PROTECT)
    character = models.CharField(max_length=500, default='', blank=True)
    billing = models.IntegerField(default=1, unique=False)

    def __str__(self):
        return (self.person.firstName + " " + self.person.surname + " || " + self.webSeries.title + " || " + self.role.role)

    def getPerson(self):
        return (self.person.firstName + " " + self.person.surname)

    class Meta:
        verbose_name = "Web Series - Person Mapping"
        verbose_name_plural = "Web Series - Person Mappings"

#---Franchises---------------------------------------------------------------------------------------------------------#
class Franchise(models.Model):
    title = models.CharField(max_length=500, default='NoFranchiseNameSpecified')
    posterFilePath = models.CharField(max_length=500, default='https://i.gyazo.com/94770d8db3ef2cf193553e34f6e29e2d.png')
    image = models.ImageField(blank=True, upload_to='franchises')
    description = models.CharField(max_length=1000, blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

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
    parentFranchise = models.ForeignKey(Franchise, on_delete=models.PROTECT)
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
    posterFilePath = models.CharField(max_length=500, default='https://i.gyazo.com/94770d8db3ef2cf193553e34f6e29e2d.png')
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
    parentFranchise = models.ForeignKey(VideoGameFranchise, on_delete=models.PROTECT)
    title = models.CharField(max_length=500, default='NoVideoGameFranchiseSubCategoryNameSpecified')
    subCategoryOrder = models.IntegerField(default=1)

    def __str__(self):
        return self.parentFranchise.title + " - " + self.title

    class Meta:
        verbose_name = "Video Game Franchise Subcategory"
        verbose_name_plural = "Video Game Franchise Subcategories"

class FilmFranchiseSubcategoryMapping(models.Model):
    film = models.ForeignKey(Film, on_delete=models.PROTECT)
    franchiseSubcategory = models.ForeignKey(FranchiseSubcategory, on_delete=models.PROTECT)
    orderInFranchise = models.IntegerField(default=1)

    def __str__(self):
        return (self.franchiseSubcategory.title + " - " + self.film.title)

    class Meta:
        verbose_name = "Films - Franchise  Subcategory Mapping"
        verbose_name_plural = "Films - Franchise  Subcategory Mappings"

class TelevisionFranchiseSubcategoryMapping(models.Model):
    television = models.ForeignKey(Television, on_delete=models.PROTECT)
    franchiseSubcategory = models.ForeignKey(FranchiseSubcategory, on_delete=models.PROTECT)
    orderInFranchise = models.IntegerField(default=1)

    def __str__(self):
        return (self.franchiseSubcategory.title + " - " + str(self.orderInFranchise) + " - " + self.television.title)

    class Meta:
        verbose_name = "Television - Franchise  Subcategory Mapping"
        verbose_name_plural = "Television - Franchise  Subcategory Mappings"

class VideoGameFranchiseSubcategoryMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.PROTECT)
    franchiseSubcategory = models.ForeignKey(VideoGameFranchiseSubcategory, on_delete=models.PROTECT)
    orderInFranchise = models.IntegerField(default=1)

    def __str__(self):
        return (self.franchiseSubcategory.title + " - " + str(self.orderInFranchise) + " - " + self.videoGame.title)

    class Meta:
        verbose_name = "Video Games - Franchise  Subcategory Mapping"
        verbose_name_plural = "Video Games - Franchise  Subcategory Mappings"

class BookFranchiseSubcategoryMapping(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    franchiseSubcategory = models.ForeignKey(FranchiseSubcategory, on_delete=models.PROTECT)
    orderInFranchise = models.IntegerField(default=1)

    def __str__(self):
        return (self.franchiseSubcategory.title + " - " + str(self.orderInFranchise) + " - " + self.book.title)

    class Meta:
        verbose_name = "Books - Franchise  Subcategory Mapping"
        verbose_name_plural = "Books - Franchise  Subcategory Mappings"

class WebSeriesFranchiseSubcategoryMapping(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.PROTECT)
    franchiseSubcategory = models.ForeignKey(FranchiseSubcategory, on_delete=models.PROTECT)
    orderInFranchise = models.IntegerField(default=1)

    def __str__(self):
        return (self.franchiseSubcategory.title + " - " + str(self.orderInFranchise) + " - " + self.webSeries.title)

    class Meta:
        verbose_name = "Web Series - Franchise  Subcategory Mapping"
        verbose_name_plural = "Web Series - Franchise  Subcategory Mappings"


#---Franchise-Genre Mappings---------------------------------------------------------------------------------------------------------#
class FranchiseGenreMapping(models.Model):
    franchise = models.ForeignKey(Franchise, on_delete=models.PROTECT)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT)

    def __str__(self):
        return (self.franchise.title + " - " + self.genre.title)

    class Meta:
        verbose_name = "Franchises - Genre Mapping"
        verbose_name_plural = "Franchises - Genre Mappings"

class VideoGameFranchiseGenreMapping(models.Model):
    franchise = models.ForeignKey(VideoGameFranchise, on_delete=models.PROTECT)
    genre = models.ForeignKey(VideoGameGenre, on_delete=models.PROTECT)

    def __str__(self):
        return (self.franchise.title + " - " + self.genre.title)

    class Meta:
        verbose_name = "Video Game Franchises - Genre Mapping"
        verbose_name_plural = "Video Game Franchises - Genre Mappings"

#---Company-Franchise Mappings---------------------------------------------------------------------------------------------------------#
class FranchiseCompanyMapping(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, default='')
    franchise = models.ForeignKey(Franchise, on_delete=models.PROTECT, default='')

    def __str__(self):
        return (self.company.name + " - " + self.franchise.title)

    class Meta:
        verbose_name = "Company - Franchise Mapping"
        verbose_name_plural = "Companies - Franchise Mappings"

class VideoGameFranchiseCompanyMapping(models.Model):
    company = models.ForeignKey(Company, on_delete=models.PROTECT, default='')
    franchise = models.ForeignKey(VideoGameFranchise, on_delete=models.PROTECT, default='')

    def __str__(self):
        return (self.company.name + " - " + self.franchise.title)

    class Meta:
        verbose_name = "Company - Video Game Franchise Mapping"
        verbose_name_plural = "Companies - Video Game Franchise Mappings"


#---Video Game Consoles and Mappings---------------------------------------------------------------------------------------------------------#
class Console(models.Model):
    name = models.CharField(max_length=500, default='NoConsoleNameSpecified')
    shortName = models.CharField(max_length=500, default='NoShortConsoleNameSpecified')
    release = models.DateField(default=timezone.now)
    developer = models.ForeignKey(Company, on_delete=models.PROTECT)
    imageFilePath = models.CharField(max_length=500,blank=True)
    slug = models.SlugField(max_length=150, blank=True, editable=True, default='')
    image = models.ImageField(blank=True, upload_to='consoles')

    def save(self, *args, **kwargs):
        super().save()
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 600:
                output_size = (600, 600)
                img.thumbnail(output_size)
                img.save(self.image.path)
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
    console = models.ForeignKey(Console, on_delete=models.PROTECT)
    release = models.DateField(default=timezone.now)
    image = models.ImageField(blank=True, upload_to='consoles')

    def save(self, *args, **kwargs):
        super().save()
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 600:
                output_size = (600, 600)
                img.thumbnail(output_size)
                img.save(self.image.path)
        super(ConsoleVersion, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Video Game Console - Version"
        verbose_name_plural = "Video Game Consoles - Versions"

class VideoGameConsoleMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.PROTECT)
    console = models.ForeignKey(Console, on_delete=models.PROTECT)

    def __str__(self):
        return (self.videoGame.title + " | " + self.console.name)

    class Meta:
        verbose_name = "Video Games - Console Mapping"
        verbose_name_plural = "Video Games - Console Mappings"


#---Awards---------------------------------------------------------------------------------------------------------#

class AwardType(models.Model):
    name = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Awards - Type"
        verbose_name_plural = "Awards - Types"

class AwardsShow(models.Model):
    name = models.CharField(max_length=50, default='')
    award = models.ForeignKey(AwardType, on_delete=models.PROTECT)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return self.name + " | " + str(self.date)

    class Meta:
        verbose_name = "Awards - Show"
        verbose_name_plural = "Awards - Shows"

class AwardsCategories(models.Model):
    name = models.CharField(max_length=50)
    awardType = models.ForeignKey(AwardType, on_delete=models.PROTECT)
    categoryOrder = models.IntegerField(default=1)
    personCompanyPriority = models.BooleanField(default=False)

    def __str__(self):
        return (self.name + " | " + self.awardType.name)

    class Meta:
        verbose_name = "Awards - Category"
        verbose_name_plural = "Awards - Categories"

#---Media Awards Mappings---------------------------------------------------------------------------------------------------------#

class FilmAwardMapping(models.Model):
    film = models.ForeignKey(Film, on_delete=models.PROTECT)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.PROTECT, default='')
    category = models.ForeignKey(AwardsCategories, on_delete=models.PROTECT, null=True)
    win = models.BooleanField(default=False)

    def __str__(self):
        return (self.film.title + " | " + self.awardsShow.name + " | " + self.category.name)

    class Meta:
        verbose_name = "Film - Award"
        verbose_name_plural = "Films - Awards"

class TelevisionAwardMapping(models.Model):
    television = models.ForeignKey(Television, on_delete=models.PROTECT)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.PROTECT, default='')
    category = models.ForeignKey(AwardsCategories, on_delete=models.PROTECT, null=True)
    win = models.BooleanField(default=False)

    def __str__(self):
        return (self.television.title + " | " + self.awardsShow.name + " | " + self.category.name)

    class Meta:
        verbose_name = "Television - Award"
        verbose_name_plural = "Television - Awards"

class VideoGameAwardMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.PROTECT)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.PROTECT, default='')
    category = models.ForeignKey(AwardsCategories, on_delete=models.PROTECT, null=True)
    win = models.BooleanField(default=False)

    def __str__(self):
        return (self.videoGame.title + " | " + self.awardsShow.name + " | " + self.category.name)

    class Meta:
        verbose_name = "Video Game - Award"
        verbose_name_plural = "Video Games - Awards"

class BookAwardMapping(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.PROTECT, default='')
    category = models.ForeignKey(AwardsCategories, on_delete=models.PROTECT, null=True)
    win = models.BooleanField(default=False)

    def __str__(self):
        return (self.book.title + " | " + self.awardsShow.name + " | " + self.category.name)

    class Meta:
        verbose_name = "Book - Award"
        verbose_name_plural = "Books - Awards"

class WebSeriesAwardMapping(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.PROTECT)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.PROTECT, default='')
    category = models.ForeignKey(AwardsCategories, on_delete=models.PROTECT, null=True)
    win = models.BooleanField(default=False)

    def __str__(self):
        return (self.webSeries.title + " | " + self.awardsShow.name + " | " + self.category.name)

    class Meta:
        verbose_name = "Web Series - Award"
        verbose_name_plural = "Web Series - Awards"

# ---Award Credit Mappings---------------------------------------------------------------------------------------------------------#

class FilmAwardCreditMapping(models.Model):
    FilmAwardMapping = models.ForeignKey(FilmAwardMapping, on_delete=models.PROTECT, default='')
    Person = models.ForeignKey(Person, on_delete=models.PROTECT, blank=True, null=True)
    Company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        if self.Person:
            return (self.FilmAwardMapping.film.title + " | " + self.FilmAwardMapping.awardsShow.name + " | " + self.Person.getFullName())
        if self.Company:
            return (self.FilmAwardMapping.film.title + " | " + self.FilmAwardMapping.awardsShow.name + " | " + self.Company.name)


    class Meta:
        verbose_name = "Film - Award Credit Mapping"
        verbose_name_plural = "Films - Award Credit Mappings"

class TelevisionAwardCreditMapping(models.Model):
    TelevisionAwardMapping = models.ForeignKey(TelevisionAwardMapping, on_delete=models.PROTECT, default='')
    Person = models.ForeignKey(Person, on_delete=models.PROTECT, default='', blank=True, null=True)
    Company = models.ForeignKey(Company, on_delete=models.PROTECT, default='', blank=True, null=True)

    def __str__(self):
        return (self.TelevisionAwardMapping.television.title + " | " + self.TelevisionAwardMapping.awardsShow.name)

    class Meta:
        verbose_name = "Television - Award Credit Mapping"
        verbose_name_plural = "Television - Award Credit Mappings"

class VideoGameAwardCreditMapping(models.Model):
    VideoGameAwardMapping = models.ForeignKey(VideoGameAwardMapping, on_delete=models.PROTECT, default='')
    Person = models.ForeignKey(Person, on_delete=models.PROTECT, default='', blank=True, null=True)
    Company = models.ForeignKey(Company, on_delete=models.PROTECT, default='', blank=True, null=True)

    def __str__(self):
        return (self.VideoGameAwardMapping.videoGame.title + " | " + self.VideoGameAwardMapping.awardsShow.name)

    class Meta:
        verbose_name = "Video Game - Award Credit Mapping"
        verbose_name_plural = "Video Games - Award Credit Mappings"

class BookAwardCreditMapping(models.Model):
    BookAwardMapping = models.ForeignKey(BookAwardMapping, on_delete=models.PROTECT, default='')
    Person = models.ForeignKey(Person, on_delete=models.PROTECT, default='', blank=True, null=True)
    Company = models.ForeignKey(Company, on_delete=models.PROTECT, default='', blank=True, null=True)

    def __str__(self):
        return (self.BookAwardMapping.book.title + " | " + self.BookAwardMapping.awardsShow.name)

    class Meta:
        verbose_name = "Book - Award Credit Mapping"
        verbose_name_plural = "Books - Award Credit Mappings"

class WebSeriesAwardCreditMapping(models.Model):
    WebSeriesAwardMapping = models.ForeignKey(WebSeriesAwardMapping, on_delete=models.PROTECT, default='')
    Person = models.ForeignKey(Person, on_delete=models.PROTECT, default='', blank=True, null=True)
    Company = models.ForeignKey(Company, on_delete=models.PROTECT, default='', blank=True, null=True)

    def __str__(self):
        return (self.WebSeriesAwardMapping.webSeries.title + " | " + self.WebSeriesAwardMapping.awardsShow.name)

    class Meta:
        verbose_name = "Web Series - Award Credit Mapping"
        verbose_name_plural = "Web Series - Award Credit Mappings"

# ---Additional Image Mappings---------------------------------------------------------------------------------------------------------#

class MiscImages(models.Model):
    filePath = models.CharField(max_length=500, default='', blank=True)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.PROTECT, null=True)
    image = models.ImageField(default='MissingIcon.png', upload_to='miscImages', blank=True)

    def __str__(self):
        return (self.awardsShow.name + " | " + str(self.id))

    class Meta:
        verbose_name = "Misc - Additional Image"
        verbose_name_plural = "Misc - Additional Images"

class PersonImages(models.Model):
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    awardsShow = models.ForeignKey(AwardsShow, on_delete=models.PROTECT, blank=True, null=True)
    image = models.ImageField(default='MissingIcon.png', upload_to='people', blank=True)

    def __str__(self):
        return (self.person.getFullName() + " | " + str(self.id))

    class Meta:
        verbose_name = "Person - Additional Image"
        verbose_name_plural = "People - Additional Images"

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.image.path)
        if img.height > 600 or img.width > 600:
            output_size = (600,600)
            img.thumbnail(output_size)
            img.save(self.image.path)

class FilmImages(models.Model):
    film = models.ForeignKey(Film, on_delete=models.PROTECT)
    filePath = models.CharField(max_length=500, default='')
    image = models.ImageField(default='MissingIcon.png', upload_to='extraImages', blank=True)

    def __str__(self):
        return (self.film.title + " | " + str(self.image))

    class Meta:
        verbose_name = "Film - Additional Image"
        verbose_name_plural = "Films - Additional Images"

class TelevisionImages(models.Model):
    television = models.ForeignKey(Television, on_delete=models.PROTECT)
    filePath = models.CharField(max_length=500, default='')
    image = models.ImageField(default='MissingIcon.png', upload_to='extraImages', blank=True)

    def __str__(self):
        return (self.television.title + " | " + str(self.id))

    class Meta:
        verbose_name = "Television - Additional Image"
        verbose_name_plural = "Television - Additional Images"

class VideoGameImages(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.PROTECT)
    filePath = models.CharField(max_length=500, default='')
    image = models.ImageField(default='MissingIcon.png', upload_to='extraImages', blank=True)

    def __str__(self):
        return (self.videoGame.title + " | " + str(self.id))

    class Meta:
        verbose_name = "Video Game - Additional Image"
        verbose_name_plural = "Video Games - Additional Images"

class BookImages(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    image = models.ImageField(default='MissingIcon.png', upload_to='extraImages', blank=True)

    def __str__(self):
        return (self.book.title + " | " + str(self.id))

    class Meta:
        verbose_name = "Book - Additional Image"
        verbose_name_plural = "Books - Additional Images"

class WebSeriesImages(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.PROTECT)
    filePath = models.CharField(max_length=500, default='')
    image = models.ImageField(default='MissingIcon.png', upload_to='extraImages', blank=True)

    def __str__(self):
        return (self.webSeries.title + " | " + str(self.id))

    class Meta:
        verbose_name = "Web Series - Additional Image"
        verbose_name_plural = "Web Series - Additional Images"


# ---Media Tags and Mappings---------------------------------------------------------------------------------------------------------#
class Tag(models.Model):
    name = models.CharField(max_length=50, default='', primary_key=True)

    def __str__(self):
        return (self.name)

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def save(self, *args, **kwargs):
        self.name = slugify(self.name)
        super(Tag, self).save(*args, **kwargs)


class FilmTagMapping(models.Model):
    film = models.ForeignKey(Film, on_delete=models.PROTECT)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)

    def __str__(self):
        return (self.tag.name + " - " + self.film.title)

    class Meta:
        verbose_name = "Film - Tag Mapping"
        verbose_name_plural = "Films - Tag Mappings"


class TelevisionTagMapping(models.Model):
    television = models.ForeignKey(Television, on_delete=models.PROTECT)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)

    def __str__(self):
        return (self.tag.name + " - " + self.television.title)

    class Meta:
        verbose_name = "Television - Tag Mapping"
        verbose_name_plural = "Television - Tag Mappings"
