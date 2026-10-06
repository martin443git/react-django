from django.db import transaction
from django.utils import timezone

from .models import Booking, Ticket


def release_expired():
    """Free the seats of unpaid reservations whose pay-by time has passed."""
    ids = list(
        Booking.objects.filter(
            status=Booking.Status.PENDING, expires_at__lt=timezone.now()
        ).values_list("id", flat=True)
    )
    if not ids:
        return
    with transaction.atomic():
        Ticket.objects.filter(booking_id__in=ids).delete()
        Booking.objects.filter(id__in=ids).update(status=Booking.Status.EXPIRED)


def release_booking(booking, new_status):
    """Cancel/expire a booking and free its seats (tickets are unique per show)."""
    with transaction.atomic():
        booking.tickets.all().delete()
        booking.status = new_status
        booking.save(update_fields=["status"])
