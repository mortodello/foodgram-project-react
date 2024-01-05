from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Tag, Ingredient, Recipe, IngredientRecipe, Favorites, ShoppingCard, Follow

from .serializers import (
    CustomUserSerializer, TagSerializer,
    IngredientSerializer, RecipeSerializer,
    IngredientRecipeSerializer
    )
from djoser.views import UserViewSet

from django.contrib.auth import get_user_model

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        for recipe in queryset:
            if Favorites.objects.filter(recipes=recipe, user=self.request.user).exists():
                recipe.is_favorited = True
            if ShoppingCard.objects.filter(recipes=recipe, user=self.request.user).exists():
                recipe.is_in_shopping_card = True
        return queryset


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        for user in queryset:
            if Follow.objects.filter(following=self.request.user, user=user).exists():
                user.is_subscribed = True
        return queryset


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination


class IngredientRecipeViewSet(viewsets.ModelViewSet):
    queryset = IngredientRecipe.objects.all()
    serializer_class = IngredientRecipeSerializer
    pagination_class = PageNumberPagination
