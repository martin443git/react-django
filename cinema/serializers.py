from rest_framework import serializers

from .models import Movie, Screen, Seat, Showtime, Theatre


class TheatreSerializer(serializers.ModelSerializer):
    screens_count = serializers.IntegerField(source="screens.count", read_only=True)

    class Meta:
        model = Theatre
        fields = ["id", "name", "address", "city", "is_active", "screens_count"]


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = "__all__"


class ScreenSerializer(serializers.ModelSerializer):
    theatre_name = serializers.CharField(source="theatre.name", read_only=True)
    seats_count = serializers.IntegerField(source="seats.count", read_only=True)

    class Meta:
        model = Screen
        fields = ["id", "theatre", "theatre_name", "name", "seats_count"]


class SeatSerializer(serializers.ModelSerializer):
    screen_name = serializers.CharField(source="screen.__str__", read_only=True)

    class Meta:
        model = Seat
        fields = ["id", "screen", "screen_name", "row_label", "number", "seat_type"]


class ShowtimeSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="movie.title", read_only=True)
    screen_name = serializers.CharField(source="screen.__str__", read_only=True)

    class Meta:
        model = Showtime
        fields = [
            "id", "movie", "movie_title", "screen", "screen_name",
            "starts_at", "base_price", "is_active",
        ]


class SeatLayoutSerializer(serializers.Serializer):
    rows = serializers.IntegerField(min_value=1, max_value=26)
    seats_per_row = serializers.IntegerField(min_value=1, max_value=50)
    premium_rows = serializers.ListField(
        child=serializers.CharField(max_length=1), required=False, default=list
    )