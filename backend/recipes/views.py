from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Tag, Ingredient, Recipe

from .serializers import (
    CustomUserSerializer, TagSerializer,
    IngredientSerializer, RecipeGetSerializer,
    RecipePostSerializer
    )
from djoser.views import UserViewSet

from django.contrib.auth import get_user_model

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeGetSerializer
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipePostSerializer
        if self.action == 'partial_update':
            return RecipePostSerializer
        return RecipeGetSerializer

    def perform_create(self, serializer):
        serializer.save(author=User.objects.get(pk=1))#self.request.user)


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination
