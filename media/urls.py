from django.urls import path, include
from . import views
from rest_framework import routers

urlpatterns = [
    #Home Page
    path('', views.home, name='media-home'),

    #Miscellaneous Pages
    path('search/', views.searchResults, name='media-search'),
    path('browse/', views.browse, name='media-browse'),
    path('data/', views.dataSources, name="data-sources"),
    path('calendar/', views.calendar, name="calendar"),
    path('top-grossing/', views.topGrossing, name='media-top-grossing'),
    path('top-rated/', views.topRated, name='media-top-rated'),

    #People
    path('person/<str:slug>', views.PersonDetailView.as_view(), name='media-person-detail'),

    #Companies
    path('company/<str:slug>', views.CompanyDetailView.as_view(), name='media-company-detail'),

    #Films
    path('films/<str:slug>', views.FilmDetailView.as_view(), name='media-film-detail'),
    path('films/<str:slug>/crew', views.FilmCrewDetailView.as_view(), name='media-film-crew-detail'),

    #Television
    path('tv/<str:slug>', views.TVDetailView.as_view(), name='media-tv-detail'),
    path('tv/<str:slug>/crew', views.TVCrewDetailView.as_view(), name='media-tv-crew-detail'),

    #Video Games
    path('video-games/<str:slug>', views.VideoGameDetailView.as_view(), name='media-videogame-detail'),
    path('video-games/<str:slug>/crew', views.VideoGameCrewDetailView.as_view(), name='media-videogame-crew-detail'),

    #Books
    path('books/<str:slug>', views.BookDetailView.as_view(), name='media-book-detail'),

    #Web Series
    path('web-series/<str:slug>', views.WebSeriesDetailView.as_view(), name='media-webseries-detail'),

    #Subsection Home Pages
    path('films/', views.filmHome, name='film-home'),
    path('tv/', views.tvHome, name='tv-home'),
    path('video-games/', views.gameHome, name='game-home'),
    path('books/', views.bookHome, name='book-home'),
    path('web-series/', views.webHome, name='web-home'),

    #Franchises
    path('franchises/', views.franchiseHome, name='media-franchise-home'),
    path('franchises/<str:slug>', views.FranchiseDetailView.as_view(), name='media-franchise-detail'),
    path('video-game-franchises/', views.videoGameFranchiseHome, name='media-videogamefranchise-home'),
    path('video-game-franchises/<str:slug>', views.VideoGameFranchiseDetailView.as_view(), name='media-videogamefranchise-detail'),

    #Genres
    path('genre/<str:slug>', views.GenreDetailView.as_view(), name='media-genre-detail'),
    path('video-game-genre/<str:slug>', views.VideoGameGenreDetailView.as_view(), name='media-gamegenre-detail'),

    #Tags
    path('tag/<str:pk>', views.TagDetailView.as_view(), name='media-tag-detail'),

    #Awards
    path('awards/', views.awardsHome, name='media-awards-home'),
    path('awards/type/<int:pk>', views.AwardsTypeDetail.as_view(), name='media-awardstype-detail'),
    path('awards/show/<int:pk>', views.AwardsShowDetail.as_view(), name='media-awardsshow-detail'),
    path('awards/category/<int:pk>', views.AwardsCategoryDetail.as_view(), name='media-awardscategory-detail'),

    #Consoles
    path('consoles/', views.consoleHome, name='media-console-home'),
    path('consoles/<str:slug>', views.ConsoleDetailView.as_view(), name='media-console-detail'),

    #Contribution - Main Tables
    path('contribute/', views.contributeHome, name='contribute-home'),
    path('contribute/film/', views.contributeBase.as_view(), name='contribute-film'),
    path('contribute/tv/', views.contributeTelevision.as_view(), name='contribute-television'),
    path('contribute/video-game/', views.contributeVideoGame.as_view(), name='contribute-video-game'),
    path('contribute/book/', views.contributeBook.as_view(), name='contribute-book'),
    path('contribute/web-series/', views.contributeWebSeries.as_view(), name='contribute-web-series'),
    path('contribute/person', views.contributePerson.as_view(), name='contribute-person'),
    path('contribute/company', views.contributeCompany.as_view(), name='contribute-company'),

    # Contribution - Film Mappings
    path('contribute/film-person', views.contributeFilmPerson.as_view(), name='contribute-film-person-map'),
    path('contribute/film-genre', views.contributeFilmGenre.as_view(), name='contribute-film-genre-map'),
    path('contribute/film-company', views.contributeFilmCompany.as_view(), name='contribute-film-company-map'),
    path('contribute/film-tag', views.contributeFilmTag.as_view(), name='contribute-film-tag-map'),

    # Contribution - Television Mappings
    path('contribute/television-person', views.contributeTelevisionPerson.as_view(), name='contribute-television-person-map'),
    path('contribute/television-genre', views.contributeTelevisionGenre.as_view(), name='contribute-television-genre-map'),
    path('contribute/television-company', views.contributeTelevisionCompany.as_view(), name='contribute-television-company-map'),
    path('contribute/television-tag', views.contributeTelevisionTag.as_view(), name='contribute-television-tag-map'),

    # Contribution - Video Game Mappings
    path('contribute/video-game-person', views.contributeVideoGamePerson.as_view(), name='contribute-vide-game-person-map'),
    path('contribute/video-game-genre', views.contributeVideoGameGenre.as_view(), name='contribute-vide-game-genre-map'),
    path('contribute/video-game-company', views.contributeVideoGameCompany.as_view(), name='contribute-vide-game-company-map'),
    path('contribute/video-game-tag', views.contributeVideoGameTag.as_view(), name='contribute-vide-game-tag-map'),
    path('contribute/video-game-console', views.contributeVideoGameConsole.as_view(), name='contribute-vide-game-console-map'),

    # Contribution - Book Mappings
    path('contribute/book-person', views.contributeBookPerson.as_view(), name='contribute-book-person-map'),
    path('contribute/book-genre', views.contributeBookGenre.as_view(), name='contribute-book-genre-map'),
    path('contribute/book-company', views.contributeBookCompany.as_view(), name='contribute-book-company-map'),
    path('contribute/book-tag', views.contributeBookTag.as_view(), name='contribute-book-tag-map'),

    # Contribution - Web Series Mappings
    path('contribute/web-series-person', views.contributeWebSeriesPerson.as_view(), name='contribute-web-series-person-map'),
    path('contribute/web-series-genre', views.contributeWebSeriesGenre.as_view(), name='contribute-web-series-genre-map'),
    path('contribute/web-series-company', views.contributeWebSeriesCompany.as_view(), name='contribute-web-series-company-map'),
    path('contribute/web-series-tag', views.contributeWebSeriesTag.as_view(), name='contribute-web-series-tag-map'),

    #Recommender System
    path('recommender/', views.recommendations, name="recommender"),
    path('recommender/detail', views.recommendationsDetail, name="recommender-detail"),
]

#REST API URLS
router = routers.DefaultRouter()
router.register('films', views.FilmSerializerView)
router.register('tv', views.TelevisionSerializerView)

urlpatterns += [
    path('api/', include(router.urls))
]