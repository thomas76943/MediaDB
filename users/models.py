from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.utils.datetime_safe import datetime

from media.models import Film, Television, VideoGame, Book, WebSeries

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='MissingIcon.png', upload_to='profile_pics')
    bio = models.CharField(max_length=500, default="", blank=True)
    country = models.CharField(max_length=25, default="", blank=True)

    def __str__(self):
        return self.user.username + " Profile"

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)

class ProfileSection(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sectionName = models.TextField(max_length=20, default='Profile Section')

    def __str__(self):
        return self.profile.user.username + " - " + self.sectionName

class ProfileSectionFilmMapping(models.Model):
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    profileSection = models.ForeignKey(ProfileSection, on_delete=models.CASCADE)
    orderInSection = models.IntegerField(default=1)

    def __str__(self):
        return self.profileSection.profile.user.username + " - " + self.profileSection.sectionName + " - " + self.film.title

    class Meta:
        verbose_name = "Profile Section - Film Mapping"
        verbose_name_plural = "Profile Sections - Films Mappings"

class ProfileSectionTelevisionMapping(models.Model):
    television = models.ForeignKey(Television, on_delete=models.CASCADE)
    profileSection = models.ForeignKey(ProfileSection, on_delete=models.CASCADE)
    orderInSection = models.IntegerField(default=1)

    def __str__(self):
        return self.profileSection.profile.user.username + " - " + self.profileSection.sectionName + " - " + self.television.title

    class Meta:
        verbose_name = "Profile Section - Television Mapping"
        verbose_name_plural = "Profile Sections - Television Mappings"

class ProfileSectionVideoGameMapping(models.Model):
    videoGame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    profileSection = models.ForeignKey(ProfileSection, on_delete=models.CASCADE)
    orderInSection = models.IntegerField(default=1)

    def __str__(self):
        return self.profileSection.profile.user.username + " - " + self.profileSection.sectionName + " - " + self.videoGame.title

    class Meta:
        verbose_name = "Profile Section - Video Game Mapping"
        verbose_name_plural = "Profile Sections - Video Games Mappings"

class ProfileSectionBookMapping(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    profileSection = models.ForeignKey(ProfileSection, on_delete=models.CASCADE)
    orderInSection = models.IntegerField(default=1)

    def __str__(self):
        return self.profileSection.profile.user.username + " - " + self.profileSection.sectionName + " - " + self.book.title

    class Meta:
        verbose_name = "Profile Section - Book Mapping"
        verbose_name_plural = "Profile Sections - Book Mappings"

class ProfileSectionWebSeriesMapping(models.Model):
    webSeries = models.ForeignKey(WebSeries, on_delete=models.CASCADE)
    profileSection = models.ForeignKey(ProfileSection, on_delete=models.CASCADE)
    orderInSection = models.IntegerField(default=1)

    def __str__(self):
        return self.profileSection.profile.user.username + " - " + self.profileSection.sectionName + " - " + self.webSeries.title

    class Meta:
        verbose_name = "Profile Section - Web Series Mapping"
        verbose_name_plural = "Profile Sections - Web Series Mappings"

class FilmRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    film = models.ForeignKey(Film, on_delete=models.PROTECT)
    rating = models.FloatField(default=1.0)
    review = models.CharField(max_length=1000, default="", blank=True)
    dateTime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + " - " + self.film.title + " - " + str(self.rating)

    class Meta:
        verbose_name = "Film - Rating"
        verbose_name_plural = "Films - Ratings"


class TelevisionRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    television = models.ForeignKey(Television, on_delete=models.PROTECT)
    rating = models.FloatField(default=1.0)
    review = models.CharField(max_length=1000, default="", blank=True)
    dateTime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + " - " + self.television.title + " - " + str(self.rating)

    class Meta:
        verbose_name = "Television - Rating"
        verbose_name_plural = "Television - Ratings"


class VideoGameRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    videoGame = models.ForeignKey(VideoGame, on_delete=models.PROTECT)
    rating = models.FloatField(default=1.0)
    review = models.CharField(max_length=1000, default="", blank=True)
    dateTime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + " - " + self.videoGame.title + " - " + str(self.rating)

    class Meta:
        verbose_name = "Video Game - Rating"
        verbose_name_plural = "Video Games - Ratings"


class BookRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    rating = models.FloatField(default=1.0)
    review = models.CharField(max_length=1000, default="", blank=True)
    dateTime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + " - " + self.book.title + " - " + str(self.rating)

    class Meta:
        verbose_name = "Book - Rating"
        verbose_name_plural = "Books - Ratings"


class WebSeriesRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    webSeries = models.ForeignKey(WebSeries, on_delete=models.PROTECT)
    rating = models.FloatField(default=1.0)
    review = models.CharField(max_length=1000, default="", blank=True)
    dateTime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + " - " + self.webSeries.title + " - " + str(self.rating)

    class Meta:
        verbose_name = "Web Series - Rating"
        verbose_name_plural = "Web Series - Ratings"


class UserListFilmMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    film = models.ForeignKey(Film, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username + " - " + self.film.title

    class Meta:
        verbose_name = "User List - Film Mapping"
        verbose_name_plural = "User List - Film Mappings"


class UserListTelevisionMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    television = models.ForeignKey(Television, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username + " - " + self.television.title

    class Meta:
        verbose_name = "User List - Television Mapping"
        verbose_name_plural = "User List - Television Mappings"


class UserListVideoGameMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    videoGame = models.ForeignKey(VideoGame, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username + " - " + self.videoGame.title

    class Meta:
        verbose_name = "User List - Video Game Mapping"
        verbose_name_plural = "User List - Video Game Mappings"


class UserListBookMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    book = models.ForeignKey(Book, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username + " - " + self.book.title

    class Meta:
        verbose_name = "User List - Book Mapping"
        verbose_name_plural = "User List - Book Mappings"


class UserListWebSeriesMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    webSeries = models.ForeignKey(WebSeries, on_delete=models.PROTECT)

    def __str__(self):
        return self.user.username + " - " + self.webSeries.title

    class Meta:
        verbose_name = "User List - Web Series Mapping"
        verbose_name_plural = "User List - Web Series Mappings"