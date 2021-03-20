from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from .serializers import UserSerializer,AuthTokenSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings


class UserCreateView(CreateAPIView):
    name = 'create'
    """user mode view set"""
    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()


class UserTokenView(ObtainAuthToken):
    """View to create a oauth token"""
    name = "token"
    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
