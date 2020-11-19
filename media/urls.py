from django.urls import path, include
from . import views
from rest_framework import routers

urlpatterns = [
    path('', views.home, name='media-home'),

    path('search/', views.searchResults, name='media-search'),
    path('browse/', views.browse, name='media-browse'),

    path('films/', views.filmHome, name='film-home'),
    path('tv/', views.tvHome, name='tv-home'),
    path('video-games/', views.gameHome, name='game-home'),
    path('books/', views.bookHome, name='book-home'),
    path('web-series/', views.webHome, name='web-home'),

    path('top-grossing/', views.topGrossing, name='media-top-grossing'),
    path('top-rated/', views.topRated, name='media-top-rated'),

    path('person/<int:pk>', views.PersonDetailView.as_view(), name='media-person-detail'),
    path('company/<str:slug>', views.CompanyDetailView.as_view(), name='media-company-detail'),

    path('films/<str:slug>', views.FilmDetailView.as_view(), name='media-film-detail'),
    path('films/<str:slug>/crew', views.FilmCrewDetailView.as_view(), name='media-film-crew-detail'),

    path('tv/<str:slug>', views.TVDetailView.as_view(), name='media-tv-detail'),
    path('video-games/<str:slug>', views.VideoGameDetailView.as_view(), name='media-videogame-detail'),
    path('books/<str:slug>', views.BookDetailView.as_view(), name='media-book-detail'),
    path('web-series/<str:slug>', views.WebSeriesDetailView.as_view(), name='media-webseries-detail'),

    path('franchises/', views.franchiseHome, name='media-franchise-home'),
    path('franchises/<str:slug>', views.FranchiseDetailView.as_view(), name='media-franchise-detail'),
    path('video-game-franchises/', views.videoGameFranchiseHome, name='media-videogamefranchise-home'),
    path('video-game-franchises/<str:slug>', views.VideoGameFranchiseDetailView.as_view(), name='media-videogamefranchise-detail'),

    path('genre/<int:pk>', views.GenreDetailView.as_view(), name='media-genre-detail'),
    path('video-game-genre/<int:pk>', views.VideoGameGenreDetailView.as_view(), name='media-gamegenre-detail'),

    path('tag/<str:pk>', views.TagDetailView.as_view(), name='media-tag-detail'),

    path('awards/', views.AwardsHome, name='media-awards-home'),
    path('awards/type/<int:pk>', views.AwardsTypeDetail.as_view(), name='media-awardstype-detail'),
    path('awards/show/<int:pk>', views.AwardsShowDetail.as_view(), name='media-awardsshow-detail'),
    path('awards/category/<int:pk>', views.AwardsCategoryDetail.as_view(), name='media-awardscategory-detail'),

    path('console/<str:slug>', views.ConsoleDetailView.as_view(), name='media-console-detail'),

    path('contribute-media/', views.contributeMedia, name='contribute-media'),

    path('contribute-person', views.contributePerson, name='contribute-person'),
    path('contribute-role', views.contributeRole, name='contribute-role'),
    path('contribute-company', views.contributeCompany, name='contribute-company'),
    path('contribute-other', views.contributeOther, name='contribute-other'),

    path('csv-upload/', views.csvUpload, name="csv-upload"),

    path('data/', views.dataSources, name="data-sources"),

]

#REST API URLS Below

router = routers.DefaultRouter()
router.register('films', views.FilmSerializerView)
router.register('tv', views.TelevisionSerializerView)

urlpatterns += [
    path('api/', include(router.urls))
]