from rest_framework import viewsets, mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.generics import ListAPIView

from .serializers import TagSerializer, IngredientSerializer, \
    RecipeSerializer, RecipeDetailSerializer, RecipeImageSerializer, \
    RecipeHistorySerializer

from core.models import Tag, Ingredient, Recipe


class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
                            mixins.ListModelMixin,
                            mixins.CreateModelMixin
                            ):
    """Base viewset for user owned recipe"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Filter query set by authenticated user"""
        queryset = self.queryset

        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', '0'))
        )
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user) \
            .order_by('-name') \
            .distinct()

    def perform_create(self, serializer):
        """set authenticated user to user field"""
        return serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeHistoryView(viewsets.GenericViewSet,
                        ListModelMixin):
    serializer_class = RecipeHistorySerializer
    queryset = Recipe.history.all()


class RecipeHistoryDetailView(viewsets.GenericViewSet,
                        RetrieveModelMixin):
    serializer_class = RecipeHistorySerializer
    queryset = Recipe.history.all()

    def retrieve(self, request, pk=None):
        records = self.get_queryset().filter(id=pk)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)


class IngredientViewSet(BaseRecipeAttrViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """Manage recipes in database"""
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, query_params):
        """Convert a list of strings to list of integers"""
        return [int(strValue) for strValue in query_params.split(',')]

    def perform_create(self, serializer):
        """Create Recipe with authenticated user"""
        return serializer.save(user=self.request.user)

    def get_queryset(self):
        """"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return serializer based on request action"""
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        elif self.action == 'upload_image':
            return RecipeImageSerializer
        else:
            return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload image to a recipe"""
        recipe = self.get_object()

        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
