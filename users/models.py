from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.utils.datetime_safe import datetime
from django.utils.text import slugify
from media.models import Film, Television, VideoGame, Book, WebSeries

#---User Profile, User Follows, Profile Sections-----------------------------------------------------------------------#
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_pics', null=True)
    bio = models.CharField(max_length=500, default="", blank=True)
    country = models.CharField(max_length=25, default="", blank=True)

    def __str__(self):
        return self.user.username + " Profile"

class UserFollows(models.Model):
    userA = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userA')
    userB = models.ForeignKey(User, on_delete=models.CASCADE, related_name='userB')

    def __str__(self):
        return self.userA.username + " follows " + self.userB.username

    class Meta:
        verbose_name = "User Follows"
        verbose_name_plural = "User Follows"

class ProfileSection(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sectionName = models.CharField(max_length=20, default='Profile Section')
    type = models.CharField(max_length=11, default='Films')
    order = models.IntegerField(default=1)
    slug = models.SlugField(max_length=150, blank=True, editable=True)

    #Overwrite save method to populate slugfield based on profile section's name and the user who created it
    def save(self, *args, **kwargs):
        super().save()
        if not self.slug:
            self.slug = slugify(self.profile.user.username + "-" + str(self.sectionName))
        super(ProfileSection, self).save(*args, **kwargs)

    def __str__(self):
        return self.profile.user.username + " - " + self.sectionName

#---Profile Section Mappings-------------------------------------------------------------------------------------------#
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

#---Rating Mappings----------------------------------------------------------------------------------------------------#
class FilmRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    rating = models.FloatField(default=1.0)
    review = models.CharField(max_length=1000, default="", blank=True)
    dateTime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + " - " + self.film.title + " - " + str(self.rating)

    class Meta:
        verbose_name = "Film - Rating"
        verbose_name_plural = "Films - Ratings"

class TelevisionRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    television = models.ForeignKey(Television, on_delete=models.CASCADE)
    rating = models.FloatField(default=1.0)
    review = models.CharField(max_length=1000, default="", blank=True)
    dateTime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + " - " + self.television.title + " - " + str(self.rating)

    class Meta:
        verbose_name = "Television - Rating"
        verbose_name_plural = "Television - Ratings"

class VideoGameRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    videoGame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)
    rating = models.FloatField(default=1.0)
    review = models.CharField(max_length=1000, default="", blank=True)
    dateTime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + " - " + self.videoGame.title + " - " + str(self.rating)

    class Meta:
        verbose_name = "Video Game - Rating"
        verbose_name_plural = "Video Games - Ratings"

class BookRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rating = models.FloatField(default=1.0)
    review = models.CharField(max_length=1000, default="", blank=True)
    dateTime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + " - " + self.book.title + " - " + str(self.rating)

    class Meta:
        verbose_name = "Book - Rating"
        verbose_name_plural = "Books - Ratings"

class WebSeriesRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    webSeries = models.ForeignKey(WebSeries, on_delete=models.CASCADE)
    rating = models.FloatField(default=1.0)
    review = models.CharField(max_length=1000, default="", blank=True)
    dateTime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.user.username + " - " + self.webSeries.title + " - " + str(self.rating)

    class Meta:
        verbose_name = "Web Series - Rating"
        verbose_name_plural = "Web Series - Ratings"

#---List Mappings------------------------------------------------------------------------------------------------------#
class UserListFilmMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " - " + self.film.title

    class Meta:
        verbose_name = "User List - Film Mapping"
        verbose_name_plural = "User List - Film Mappings"

class UserListTelevisionMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    television = models.ForeignKey(Television, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " - " + self.television.title

    class Meta:
        verbose_name = "User List - Television Mapping"
        verbose_name_plural = "User List - Television Mappings"

class UserListVideoGameMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    videoGame = models.ForeignKey(VideoGame, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " - " + self.videoGame.title

    class Meta:
        verbose_name = "User List - Video Game Mapping"
        verbose_name_plural = "User List - Video Game Mappings"

class UserListBookMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " - " + self.book.title

    class Meta:
        verbose_name = "User List - Book Mapping"
        verbose_name_plural = "User List - Book Mappings"

class UserListWebSeriesMapping(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    webSeries = models.ForeignKey(WebSeries, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username + " - " + self.webSeries.title

    class Meta:
        verbose_name = "User List - Web Series Mapping"
        verbose_name_plural = "User List - Web Series Mappings"

#------ Film Recommendation and User Similarity Stores-----------------------------------------------------------------#
class FilmRecommendations(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    films = models.TextField(max_length=250, default="")

    def __str__(self):
        return (self.user.username + " - " + str(self.films))

    class Meta:
        verbose_name = "User - Film Recommendation"
        verbose_name_plural = "User - Film Recommendations"

class UserUserSimilarities(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    users = models.TextField(max_length=250, default="")

    def __str__(self):
        return (self.user.username + " - " + str(self.users))

    class Meta:
        verbose_name = "User - User Similarity"
        verbose_name_plural = "User - User Similarities"