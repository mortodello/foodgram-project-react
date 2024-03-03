from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import (Favorites, Follow, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCard, Tag)
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeSerializer,
                          TagSerializer, FollowSerializer)

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('tags',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
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

    @action(detail=True, methods=['get', 'post', 'delete'])
    def favorite(self, request, pk):
        Favorites.objects.create(user=self.request.user, recipes=Recipe.objects.get(id=pk))
        serializer = RecipeSerializer(Recipe.objects.get(id=pk),
                                      context={'request': request})
        return Response(serializer.data)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageNumberPagination

    @action(detail=False, methods=['get',])
    def subscriptions(self, request):
        user = User.objects.get(username=self.request.user)
        users = user.followers.all()
        serializer = FollowSerializer([User.objects.get(pk=user.following.id) for user in users],
                                      context={'request': request},
                                      many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post', 'delete'])
    def subscribe(self, request, id):
        Follow.objects.create(user=self.request.user, following=User.objects.get(pk=id))
        serializer = FollowSerializer(User.objects.get(pk=id),
                                      context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = PageNumberPagination


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = PageNumberPagination
