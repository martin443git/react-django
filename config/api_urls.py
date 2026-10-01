from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.api_views import (
    AdminLoginView,
    AdminUserViewSet,
    LoginView,
    MeView,
    RegisterView,
)
from bookings.api_views import AdminBookingViewSet, DashboardView
from cinema.api_views import (
    MovieViewSet,
    ScreenViewSet,
    SeatViewSet,
    ShowtimeViewSet,
    TheatreViewSet,
)

router = DefaultRouter()
router.register("admin/theatres", TheatreViewSet, basename="admin-theatre")
router.register("admin/movies", MovieViewSet, basename="admin-movie")
router.register("admin/screens", ScreenViewSet, basename="admin-screen")
router.register("admin/seats", SeatViewSet, basename="admin-seat")
router.register("admin/shows", ShowtimeViewSet, basename="admin-show")
router.register("admin/bookings", AdminBookingViewSet, basename="admin-booking")
router.register("admin/users", AdminUserViewSet, basename="admin-user")

urlpatterns = [
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),
    path("auth/admin-login/", AdminLoginView.as_view()),
    path("auth/refresh/", TokenRefreshView.as_view()),
    path("auth/me/", MeView.as_view()),
    path("admin/dashboard/", DashboardView.as_view()),
] + router.urls