from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


#People
admin.site.register(Person)
admin.site.register(PersonRole)

#Companies
admin.site.register(Company)
admin.site.register(CompanyRole)

#Media Types
@admin.register(Film)
class FilmAdmin(ImportExportModelAdmin):
    pass

admin.site.register(Television)
admin.site.register(VideoGame)
admin.site.register(Book)
admin.site.register(WebSeries)

#Genre Types
admin.site.register(Genre)
admin.site.register(VideoGameGenre)

#Genre Mappings
admin.site.register(FilmGenreMapping)
admin.site.register(TelevisionGenreMapping)
admin.site.register(VideoGameGenreMapping)
admin.site.register(BookGenreMapping)
admin.site.register(WebSeriesGenreMapping)

#Company Mappings
admin.site.register(FilmCompanyMapping)
admin.site.register(TelevisionCompanyMapping)
admin.site.register(VideoGameCompanyMapping)
admin.site.register(BookCompanyMapping)
admin.site.register(WebSeriesCompanyMapping)

#People Mappings
admin.site.register(FilmPersonMapping)
admin.site.register(TelevisionPersonMapping)
admin.site.register(VideoGamePersonMapping)
admin.site.register(BookPersonMapping)
admin.site.register(WebSeriesPersonMapping)

#Franchises
admin.site.register(Franchise)
admin.site.register(VideoGameFranchise)

#Franchise Genre Mappings
admin.site.register(FranchiseGenreMapping)
admin.site.register(VideoGameFranchiseGenreMapping)

#Company Franchise Mappings
admin.site.register(FranchiseCompanyMapping)
admin.site.register(VideoGameFranchiseCompanyMapping)

#Franchise Subcategory Mappings
admin.site.register(FranchiseSubcategory)
admin.site.register(VideoGameFranchiseSubcategory)
admin.site.register(FilmFranchiseSubcategoryMapping)
admin.site.register(TelevisionFranchiseSubcategoryMapping)
admin.site.register(VideoGameFranchiseSubcategoryMapping)
admin.site.register(VideoGameVideoGameFranchiseSubcategoryMapping)
admin.site.register(BookFranchiseSubcategoryMapping)
admin.site.register(WebSeriesFranchiseSubcategoryMapping)

#Consoles
admin.site.register(Console)
admin.site.register(ConsoleVersion)
admin.site.register(VideoGameConsoleMapping)

#Additional Images
admin.site.register(MiscImages)
admin.site.register(PersonImages)
admin.site.register(FilmImages)
admin.site.register(TelevisionImages)
admin.site.register(VideoGameImages)
admin.site.register(BookImages)
admin.site.register(WebSeriesImages)

#Awards
admin.site.register(AwardType)
admin.site.register(AwardsShow)
admin.site.register(AwardsCategories)

#Media Award Mappings
admin.site.register(FilmAwardMapping)
admin.site.register(TelevisionAwardMapping)
admin.site.register(VideoGameAwardMapping)
admin.site.register(BookAwardMapping)
admin.site.register(WebSeriesAwardMapping)

#Award Credits Mappings
admin.site.register(FilmAwardCreditMapping)
admin.site.register(TelevisionAwardCreditMapping)
admin.site.register(VideoGameAwardCreditMapping)
admin.site.register(BookAwardCreditMapping)
admin.site.register(WebSeriesAwardCreditMapping)

#Tag Mappings
admin.site.register(Tag)
admin.site.register(FilmTagMapping)
admin.site.register(TelevisionTagMapping)


#Highest Rating Stores
admin.site.register(HighestRatedFilms)
admin.site.register(HighestRatedTelevision)
admin.site.register(HighestRatedVideoGames)
admin.site.register(HighestRatedBooks)
admin.site.register(HighestRatedWebSeries)
