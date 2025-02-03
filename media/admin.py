from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


#People
@admin.register(Person)
class PersonAdmin(ImportExportModelAdmin):
    pass

admin.site.register(PersonRole)
admin.site.register(Department)


#Companies
admin.site.register(Company)
admin.site.register(CompanyRole)

#Media Types
@admin.register(Film)
class FilmAdmin(ImportExportModelAdmin):
    pass
@admin.register(Television)
class TelevisionAdmin(ImportExportModelAdmin):
    pass
@admin.register(TelevisionSeason)
class TelevisionSeasonAdmin(ImportExportModelAdmin):
    pass
@admin.register(TelevisionEpisode)
class TelevisionEpisodeAdmin(ImportExportModelAdmin):
    pass
@admin.register(VideoGame)
class VideoGameAdmin(ImportExportModelAdmin):
    pass
@admin.register(Book)
class BookAdmin(ImportExportModelAdmin):
    pass
@admin.register(WebSeries)
class WebSeriesAdmin(ImportExportModelAdmin):
    pass


#Genre Types
admin.site.register(Genre)
@admin.register(VideoGameGenre)
class VideoGameGenre(ImportExportModelAdmin):
    pass
admin.site.register(BookGenre)

#Genre Mappings
@admin.register(FilmGenreMapping)
class FilmGenreMappingAdmin(ImportExportModelAdmin):
    pass
admin.site.register(TelevisionGenreMapping)
admin.site.register(VideoGameGenreMapping)
admin.site.register(BookGenreMapping)
admin.site.register(WebSeriesGenreMapping)

#Company Mappings
@admin.register(FilmCompanyMapping)
class FilmCompanyMappingAdmin(ImportExportModelAdmin):
    pass

admin.site.register(TelevisionCompanyMapping)
admin.site.register(VideoGameCompanyMapping)
admin.site.register(BookCompanyMapping)
admin.site.register(WebSeriesCompanyMapping)

#People Mappings
@admin.register(FilmPersonMapping)
class FilmPersonMappingAdmin(ImportExportModelAdmin):
    pass
@admin.register(TelevisionPersonMapping)
class TelevisionPersonMappingAdmin(ImportExportModelAdmin):
    pass
@admin.register(TelevisionEpisodePersonMapping)
class TelevisionEpisodePersonMappingAdmin(ImportExportModelAdmin):
    pass
@admin.register(VideoGamePersonMapping)
class VideoGamePersonMappingAdmin(ImportExportModelAdmin):
    pass
@admin.register(BookPersonMapping)
class BookPersonMappingAdmin(ImportExportModelAdmin):
    pass
@admin.register(WebSeriesPersonMapping)
class WebSeriesPersonMappingAdmin(ImportExportModelAdmin):
    pass

#Franchises
@admin.register(Franchise)
class Franchise(ImportExportModelAdmin):
    pass
@admin.register(VideoGameFranchise)
class VideoGameFranchise(ImportExportModelAdmin):
    pass
#Franchise Genre Mappings
@admin.register(FranchiseGenreMapping)
class FranchiseGenreMapping(ImportExportModelAdmin):
    pass
@admin.register(VideoGameFranchiseGenreMapping)
class VideoGameFranchiseGenreMapping(ImportExportModelAdmin):
    pass

#Company Franchise Mappings
admin.site.register(FranchiseCompanyMapping)
admin.site.register(VideoGameFranchiseCompanyMapping)

#Franchise Subcategory Mappings
@admin.register(FranchiseSubcategory)
class FranchiseSubcategory(ImportExportModelAdmin):
    pass
@admin.register(VideoGameFranchiseSubcategory)
class VideoGameFranchiseSubcategory(ImportExportModelAdmin):
    pass
@admin.register(FilmFranchiseSubcategoryMapping)
class FilmFranchiseSubcategoryMappingAdmin(ImportExportModelAdmin):
    pass

admin.site.register(TelevisionFranchiseSubcategoryMapping)
admin.site.register(VideoGameFranchiseSubcategoryMapping)
admin.site.register(VideoGameVideoGameFranchiseSubcategoryMapping)
admin.site.register(BookFranchiseSubcategoryMapping)
admin.site.register(WebSeriesFranchiseSubcategoryMapping)

#Consoles
@admin.register(Console)
class Console(ImportExportModelAdmin):
    pass
@admin.register(ConsoleVersion)
class ConsoleVersion(ImportExportModelAdmin):
    pass
@admin.register(VideoGameConsoleMapping)
class VideoGameConsoleMapping(ImportExportModelAdmin):
    pass

#Additional Images
admin.site.register(MiscImages)
admin.site.register(PersonImages)
@admin.register(FilmImages)
class FilmImagesAdmin(ImportExportModelAdmin):
    pass
admin.site.register(TelevisionImages)
admin.site.register(VideoGameImages)
admin.site.register(BookImages)
admin.site.register(WebSeriesImages)

#Awards
admin.site.register(AwardType)
admin.site.register(AwardsShow)
admin.site.register(AwardsCategories)

#Media Award Mappings
@admin.register(FilmAwardMapping)
class FilmAwardMappingAdmin(ImportExportModelAdmin):
    pass
admin.site.register(TelevisionAwardMapping)
admin.site.register(VideoGameAwardMapping)
admin.site.register(BookAwardMapping)
admin.site.register(WebSeriesAwardMapping)

#Award Credits Mappings
@admin.register(FilmAwardCreditMapping)
class FilmAwardCreditMappingAdmin(ImportExportModelAdmin):
    pass
admin.site.register(TelevisionAwardCreditMapping)
admin.site.register(VideoGameAwardCreditMapping)
admin.site.register(BookAwardCreditMapping)
admin.site.register(WebSeriesAwardCreditMapping)

#Tag Mappings
admin.site.register(Tag)
@admin.register(FilmTagMapping)
class FilmTagMappingAdmin(ImportExportModelAdmin):
    pass
admin.site.register(TelevisionTagMapping)
admin.site.register(VideoGameTagMapping)
admin.site.register(BookTagMapping)
admin.site.register(WebSeriesTagMapping)


#Highest Rating Stores
@admin.register(HighestRatedFilms)
class HighestRatedFilmsAdmin(ImportExportModelAdmin):
    pass
admin.site.register(HighestRatedTelevision)
admin.site.register(HighestRatedVideoGames)
admin.site.register(HighestRatedBooks)
admin.site.register(HighestRatedWebSeries)


# Profile Sections
