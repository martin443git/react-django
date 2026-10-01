from rest_framework import serializers

from .models import Booking, Ticket


class TicketSerializer(serializers.ModelSerializer):
    seat_label = serializers.CharField(source="seat.__str__", read_only=True)

    class Meta:
        model = Ticket
        fields = ["id", "seat", "seat_label", "price"]


class AdminBookingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    movie_title = serializers.CharField(source="showtime.movie.title", read_only=True)
    starts_at = serializers.DateTimeField(source="showtime.starts_at", read_only=True)
    tickets = TicketSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id", "username", "movie_title", "starts_at", "status",
            "total", "created_at", "tickets",
        ]