from django.contrib import admin

from .models import Booking, Ticket


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "showtime", "status", "total", "created_at"]
    list_filter = ["status"]
    inlines = [TicketInline]