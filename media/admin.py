from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


#People
@admin.register(Person)
class PersonAdmin(ImportExportModelAdmin):
    pass

admin.site.register(PersonRole)

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
admin.site.register(VideoGameGenre)
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
@admin.register(FilmFranchiseSubcategoryMapping)
class FilmFranchiseSubcategoryMappingAdmin(ImportExportModelAdmin):
    pass

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
