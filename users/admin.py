from django.contrib import admin
from .models import *

admin.site.register(Profile)

admin.site.register(UserFollows)

admin.site.register(FilmRating)
admin.site.register(TelevisionRating)
admin.site.register(VideoGameRating)
admin.site.register(BookRating)
admin.site.register(WebSeriesRating)

admin.site.register(ProfileSection)
admin.site.register(ProfileSectionFilmMapping)
admin.site.register(ProfileSectionTelevisionMapping)
admin.site.register(ProfileSectionVideoGameMapping)
admin.site.register(ProfileSectionBookMapping)
admin.site.register(ProfileSectionWebSeriesMapping)

admin.site.register(UserListFilmMapping)
admin.site.register(UserListTelevisionMapping)
admin.site.register(UserListVideoGameMapping)
admin.site.register(UserListBookMapping)
admin.site.register(UserListWebSeriesMapping)
