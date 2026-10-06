from django.db.models import Sum
from django.utils import timezone
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from cinema.models import Movie, Showtime, Theatre

from .models import Booking
from .serializers import AdminBookingSerializer
from .services import release_booking, release_expired


class BookingSearch(filters.SearchFilter):
    """Staff can type a booking code like TB-12 (or just 12) at the counter."""

    def filter_queryset(self, request, queryset, view):
        term = request.query_params.get("search", "").strip().upper().replace("TB-", "")
        if term.isdigit():
            return queryset.filter(pk=int(term))
        return super().filter_queryset(request, queryset, view)


class AdminBookingViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminBookingSerializer
    filter_backends = [BookingSearch]
    search_fields = ["user__username", "showtime__movie__title"]

    def get_queryset(self):
        release_expired()
        qs = (
            Booking.objects.select_related("user", "showtime__movie")
            .prefetch_related("tickets__seat")
            .order_by("-created_at")
        )
        status = self.request.query_params.get("status")
        return qs.filter(status=status) if status else qs

    @action(detail=True, methods=["post"], url_path="mark-paid")
    def mark_paid(self, request, pk=None):
        booking = self.get_object()
        if booking.status != Booking.Status.PENDING:
            return Response({"detail": f"This booking is {booking.status.lower()}."}, status=400)
        booking.status = Booking.Status.CONFIRMED
        booking.expires_at = None
        booking.save(update_fields=["status", "expires_at"])
        return Response({"status": booking.status})

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.status in (Booking.Status.CANCELLED, Booking.Status.EXPIRED):
            return Response({"detail": f"This booking is already {booking.status.lower()}."}, status=400)
        release_booking(booking, Booking.Status.CANCELLED)
        return Response({"status": booking.status})


class DashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.localdate()
        confirmed = Booking.objects.filter(status=Booking.Status.CONFIRMED)
        return Response({
            "theatres": Theatre.objects.count(),
            "movies": Movie.objects.count(),
            "shows": Showtime.objects.count(),
            "bookings": confirmed.count(),
            "users": User.objects.count(),
            "todays_bookings": confirmed.filter(created_at__date=today).count(),
            "revenue": confirmed.aggregate(total=Sum("total"))["total"] or 0,
        })
