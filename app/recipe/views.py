# Views for recipe API

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from recipe import serializers


class BaseRecipeAttrViewSet(mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin,
                            viewsets.GenericViewSet):
    # Base ViewSets for recipe attribute
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage Recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        recipes = self.queryset.filter(user=self.request.user).order_by('-id')
        return recipes

    def get_serializer_class(self):
        # return the serializer class for request

        if self.action == 'list':
            return serializers.RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        # Create a new Recipe.
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage Tags in DataBase"""
    serializer_class = serializers.TagsSerializer
    queryset = Tag.objects.all()


class IngredientsViewSets(BaseRecipeAttrViewSet):
    """Manage Ingredients in the DataBase"""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
