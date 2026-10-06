from django.urls import path

from . import public_views as v

urlpatterns = [
    path("shows/<int:pk>/seats/", v.SeatMapView.as_view()),
    path("shows/<int:pk>/reserve/", v.ReserveView.as_view()),
    path("my/bookings/", v.MyBookingsView.as_view()),
    path("bookings/<int:pk>/", v.BookingDetailView.as_view()),
    path("bookings/<int:pk>/cancel/", v.BookingCancelView.as_view()),
]
