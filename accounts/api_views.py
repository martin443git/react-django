from rest_framework import filters, generics, viewsets
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (
    AdminLoginSerializer,
    AdminUserSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserSerializer,
)

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer


class AdminLoginView(TokenObtainPairView):
    serializer_class = AdminLoginSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
class AdminUserViewSet(viewsets.ModelViewSet):
    """List, view and edit users (activate/deactivate). No create or delete here."""
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "email"]
    http_method_names = ["get", "patch", "head", "options"]