from django.utils import timezone
from rest_framework import generics, serializers
from rest_framework.permissions import AllowAny

from .models import Movie, Screen, Showtime, Theatre


class PublicMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ["id", "title", "description", "duration_minutes",
                  "language", "rating", "release_date"]


class PublicTheatreSerializer(serializers.ModelSerializer):
    screens_count = serializers.SerializerMethodField()

    class Meta:
        model = Theatre
        fields = ["id", "name", "city", "address", "screens_count"]

    def get_screens_count(self, obj):
        return Screen.objects.filter(theatre=obj).count()


class PublicShowSerializer(serializers.ModelSerializer):
    theatre_name = serializers.CharField(source="screen.theatre.name", read_only=True)
    screen_name = serializers.CharField(source="screen.name", read_only=True)
    movie_title = serializers.CharField(source="movie.title", read_only=True)

    class Meta:
        model = Showtime
        fields = ["id", "movie", "movie_title", "screen", "screen_name",
                  "theatre_name", "starts_at", "base_price"]


class Public:
    # No login needed to browse. authentication_classes = [] stops an old or
    # expired customer token from blocking anonymous visitors.
    permission_classes = [AllowAny]
    authentication_classes = []
    pagination_class = None


class MovieList(Public, generics.ListAPIView):
    serializer_class = PublicMovieSerializer
    queryset = Movie.objects.filter(is_active=True).order_by("-release_date", "title")


class MovieDetail(Public, generics.RetrieveAPIView):
    serializer_class = PublicMovieSerializer
    queryset = Movie.objects.filter(is_active=True)


class TheatreList(Public, generics.ListAPIView):
    serializer_class = PublicTheatreSerializer
    queryset = Theatre.objects.filter(is_active=True).order_by("city", "name")


class MovieShows(Public, generics.ListAPIView):
    serializer_class = PublicShowSerializer

    def get_queryset(self):
        qs = (Showtime.objects
              .filter(movie_id=self.kwargs["pk"], is_active=True,
                      starts_at__gte=timezone.now())
              .select_related("screen__theatre", "movie")
              .order_by("starts_at"))
        date = self.request.query_params.get("date")
        if date:
            qs = qs.filter(starts_at__date=date)
        return qs