from django.db.models import Sum
from django.utils import timezone
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from cinema.models import Movie, Showtime, Theatre

from .models import Booking
from .serializers import AdminBookingSerializer


class AdminBookingViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    serializer_class = AdminBookingSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["user__username", "showtime__movie__title"]

    def get_queryset(self):
        qs = (
            Booking.objects.select_related("user", "showtime__movie")
            .prefetch_related("tickets__seat")
            .order_by("-created_at")
        )
        status = self.request.query_params.get("status")
        return qs.filter(status=status) if status else qs


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