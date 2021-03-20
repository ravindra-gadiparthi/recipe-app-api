from django.contrib.auth import get_user_model
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings

from .serializers import UserSerializer, AuthTokenSerializer


class UserCreateView(CreateAPIView):
    """user mode view set"""
    name = 'create'
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()


class ManageUserView(RetrieveUpdateAPIView):
    name = "manage"
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_object(self):
        """retrieve authenticated user"""
        return self.request.user


class UserTokenView(ObtainAuthToken):
    """View to create a oauth token"""
    name = "token"
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
