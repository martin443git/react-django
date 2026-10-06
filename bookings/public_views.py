from datetime import timedelta
from decimal import Decimal

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cinema.models import Seat, Showtime

from .models import Booking, Ticket
from .services import release_booking, release_expired

PREMIUM_EXTRA = Decimal("100")              # added to base_price for premium seats
RELEASE_BEFORE_SHOW = timedelta(minutes=30)  # unpaid seats are released this long before the show
BOOKING_CLOSES = timedelta(minutes=60)       # no online reservations this close to the show
MAX_SEATS = 8


def seat_price(show, seat):
    return show.base_price + (PREMIUM_EXTRA if seat.seat_type == Seat.SeatType.PREMIUM else 0)


def booking_qs():
    return Booking.objects.select_related(
        "showtime__movie", "showtime__screen__theatre"
    ).prefetch_related("tickets__seat")


def booking_data(b):
    s = b.showtime
    return {
        "id": b.id, "code": f"TB-{b.id}", "status": b.status, "total": str(b.total),
        "expires_at": b.expires_at, "created_at": b.created_at,
        "movie_title": s.movie.title, "theatre_name": s.screen.theatre.name,
        "screen_name": s.screen.name, "starts_at": s.starts_at,
        "seats": [f"{t.seat.row_label}{t.seat.number}" for t in b.tickets.all()],
    }


class SeatMapView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, pk):
        release_expired()
        show = get_object_or_404(
            Showtime.objects.select_related("movie", "screen__theatre"), pk=pk, is_active=True
        )
        taken = set(Ticket.objects.filter(showtime=show).values_list("seat_id", flat=True))
        seats = Seat.objects.filter(screen=show.screen)
        return Response({
            "show": {"id": show.id, "movie_title": show.movie.title, "starts_at": show.starts_at,
                     "theatre_name": show.screen.theatre.name, "screen_name": show.screen.name},
            "seats": [{"id": s.id, "row": s.row_label, "number": s.number, "type": s.seat_type,
                       "price": str(seat_price(show, s)), "booked": s.id in taken} for s in seats],
        })


class ReserveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        ids = request.data.get("seat_ids")
        if not isinstance(ids, list) or not ids or len(set(ids)) > MAX_SEATS:
            return Response({"detail": f"Choose 1 to {MAX_SEATS} seats."}, status=400)
        release_expired()
        try:
            with transaction.atomic():
                # Locking the show row makes concurrent reservations for it run one at a time.
                show = Showtime.objects.select_for_update().filter(pk=pk, is_active=True).first()
                if not show:
                    return Response({"detail": "Show not found."}, status=404)
                if show.starts_at - BOOKING_CLOSES < timezone.now():
                    return Response({"detail": "Online booking for this show has closed."}, status=400)
                seats = list(Seat.objects.filter(id__in=ids, screen=show.screen))
                if len(seats) != len(set(ids)):
                    return Response({"detail": "Some seats are not valid for this show."}, status=400)
                if Ticket.objects.filter(showtime=show, seat__in=seats).exists():
                    return Response({"detail": "Some of those seats were just taken. Pick different seats."}, status=409)
                booking = Booking.objects.create(
                    user=request.user, showtime=show, status=Booking.Status.PENDING,
                    expires_at=show.starts_at - RELEASE_BEFORE_SHOW,
                )
                tickets = [Ticket(booking=booking, showtime=show, seat=s, price=seat_price(show, s)) for s in seats]
                Ticket.objects.bulk_create(tickets)
                booking.total = sum((t.price for t in tickets), Decimal("0"))
                booking.save(update_fields=["total"])
        except IntegrityError:
            return Response({"detail": "Some of those seats were just taken. Pick different seats."}, status=409)
        return Response(booking_data(booking_qs().get(pk=booking.pk)), status=201)


class MyBookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        release_expired()
        qs = booking_qs().filter(user=request.user).order_by("-created_at")
        return Response([booking_data(b) for b in qs])


class BookingDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        release_expired()
        return Response(booking_data(get_object_or_404(booking_qs(), pk=pk, user=request.user)))


class BookingCancelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        b = get_object_or_404(Booking, pk=pk, user=request.user)
        if b.status != Booking.Status.PENDING:
            return Response({"detail": "Only unpaid reservations can be cancelled online. Please contact the theatre."}, status=400)
        release_booking(b, Booking.Status.CANCELLED)
        return Response(booking_data(booking_qs().get(pk=pk)))
