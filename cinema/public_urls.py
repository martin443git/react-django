from django.urls import path

from . import public_views as v

urlpatterns = [
    path("movies/", v.MovieList.as_view()),
    path("movies/<int:pk>/", v.MovieDetail.as_view()),
    path("movies/<int:pk>/shows/", v.MovieShows.as_view()),
    path("theatres/", v.TheatreList.as_view()),
]
