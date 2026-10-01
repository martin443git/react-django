from django.contrib import admin

from .models import Movie, Screen, Seat, Showtime, Theatre


@admin.register(Theatre)
class TheatreAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "is_active"]
    search_fields = ["name", "city"]


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ["title", "language", "duration_minutes", "is_active"]
    search_fields = ["title"]


@admin.register(Screen)
class ScreenAdmin(admin.ModelAdmin):
    list_display = ["name", "theatre"]


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ["screen", "row_label", "number", "seat_type"]
    list_filter = ["screen", "seat_type"]


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ["movie", "screen", "starts_at", "base_price", "is_active"]
    list_filter = ["movie", "is_active"]