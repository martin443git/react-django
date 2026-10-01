import string

from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import Movie, Screen, Seat, Showtime, Theatre
from .serializers import (
    MovieSerializer,
    ScreenSerializer,
    SeatLayoutSerializer,
    SeatSerializer,
    ShowtimeSerializer,
    TheatreSerializer,
)


class AdminBase(viewsets.ModelViewSet):
    """Staff-only CRUD with search and ordering."""
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]


class TheatreViewSet(AdminBase):
    queryset = Theatre.objects.all().order_by("-id")
    serializer_class = TheatreSerializer
    search_fields = ["name", "city"]


class MovieViewSet(AdminBase):
    queryset = Movie.objects.all().order_by("-id")
    serializer_class = MovieSerializer
    search_fields = ["title", "language"]


class ScreenViewSet(AdminBase):
    queryset = Screen.objects.select_related("theatre").order_by("-id")
    serializer_class = ScreenSerializer
    search_fields = ["name", "theatre__name"]

    @action(detail=True, methods=["post"], url_path="generate-seats")
    def generate_seats(self, request, pk=None):
        """Create a full seat layout, e.g. {"rows": 8, "seats_per_row": 12, "premium_rows": ["G", "H"]}"""
        screen = self.get_object()
        serializer = SeatLayoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        premium = {r.upper() for r in data["premium_rows"]}
        row_labels = string.ascii_uppercase[: data["rows"]]
        seats = [
            Seat(
                screen=screen,
                row_label=row,
                number=number,
                seat_type=Seat.SeatType.PREMIUM if row in premium else Seat.SeatType.STANDARD,
            )
            for row in row_labels
            for number in range(1, data["seats_per_row"] + 1)
        ]
        Seat.objects.bulk_create(seats, ignore_conflicts=True)
        return Response({"total_seats": screen.seats.count()})


class SeatViewSet(AdminBase):
    serializer_class = SeatSerializer
    search_fields = ["row_label"]

    def get_queryset(self):
        qs = Seat.objects.select_related("screen__theatre").order_by("screen", "row_label", "number")
        screen = self.request.query_params.get("screen")
        return qs.filter(screen_id=screen) if screen else qs


class ShowtimeViewSet(AdminBase):
    queryset = Showtime.objects.select_related("movie", "screen__theatre").order_by("-starts_at")
    serializer_class = ShowtimeSerializer
    search_fields = ["movie__title", "screen__name", "screen__theatre__name"]