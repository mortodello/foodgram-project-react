from django.contrib.auth import get_user_model
from django.db.models import Count
from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import CreateAPIView

from .models import (Favorites, Follow, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCard, Tag)
from .serializers import (CustomUserSerializer, IngredientRecipeSerializer,
                          IngredientSerializer, RecipeSerializer,
                          TagSerializer, FollowSerializer,
                          FavoritesSerializer)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        for recipe in queryset:
            if Favorites.objects.filter(recipes=recipe,
                                        user=self.request.user).exists():
                recipe.is_favorited = True
            if ShoppingCard.objects.filter(recipes=recipe,
                                           user=self.request.user).exists():
                recipe.is_in_shopping_card = True
        return queryset


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        queryset = User.objects.all()
        for user in queryset:
            if Follow.objects.filter(following=self.request.user,
                                     user=user).exists():
                user.is_subscribed = True
        return queryset


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer

    def get_queryset(self):
        user = User.objects.get(username=self.request.user)
        users = user.followers.all()
        queryset = []
        id_set = []
        for user in users:
            id_set.append(user.following.id)
        for id in id_set:
            queryset.append(User.objects.get(pk=id))
        return queryset


class FavoritesViewSet(viewsets.ModelViewSet):
    serializer_class = FavoritesSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Recipe.objects.filter(pk=self.kwargs['id'])

    def create(self, request, *args, **kwargs):
        recipe = Recipe.objects.get(pk=request.id)
        return Favorites.objects.create(user=request.user, recipes=recipe)


class FavoriteView(CreateAPIView):
    def get_serializer(self, *args, **kwargs):
        serializer_class = RecipeSerializer
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        print(kwargs['id'])
        #serializer = self.get_serializer(data=request.data)
        #serializer.is_valid(raise_exception=True)
        #print(serializer.data)
        recipe = Recipe.objects.get(pk=kwargs['id'])
        Favorites.objects.create(user=request.user, recipes=recipe)
        #headers = self.get_success_headers(serializer.data)
        #print(recipe.__dict__)
        serializer = FavoritesSerializer(instance=recipe)
        #serializer.is_valid(raise_exception=True)
        #print(serializer.data)
        #serializer.data.pop('tags')
        #serializer.data.pop('author')
        #serializer.data.pop('ingredients')
        #serializer.data.pop('is_favorited')
        #serializer.data.pop('is_in_shopping_card')
        #serializer.data.pop('text')
        #print(serializer.data['author'])
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
