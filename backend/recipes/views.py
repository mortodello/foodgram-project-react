from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (FavoriteSerializer, FoodgramUserSerializer,
                          IngredientSerializer, RecipeSerializer,
                          ShoppigCartSerializer, SubscriptionsPostSerializer,
                          SubscriptionsSerializer, TagSerializer)
from users.models import Subscriptions

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = (IsAdminAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', ],
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, pk):
        serializer = FavoriteSerializer(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer_recipe = RecipeSerializer(Recipe.objects.get(id=pk),
                                             context={'request': request})
        return Response(serializer_recipe.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if not Favorite.objects.filter(user__id=request.user.id,
                                       recipe=recipe).exists():
            return Response({'errors': 'Такого рецепта нет в избранном!'},
                            status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.filter(user__id=request.user.id,
                                recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', ],
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, pk):
        serializer = ShoppigCartSerializer(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer_recipe = RecipeSerializer(Recipe.objects.get(id=pk),
                                             context={'request': request})
        return Response(serializer_recipe.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if not Favorite.objects.filter(user__id=request.user.id,
                                       recipe=recipe).exists():
            return Response({'errors': 'Такого рецепта нет в списке покупок!'},
                            status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.filter(user__id=request.user.id,
                                    recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).order_by(
            'ingredient__name'
        ).annotate(ingredient_amount=Sum('amount'))
        shopping_list = ['Список покупок:\n']
        for ingredient in ingredients:
            name = ingredient['ingredient__name']
            unit = ingredient['ingredient__measurement_unit']
            amount = ingredient['ingredient_amount']
            shopping_list.append(f'\n{name} - {amount}, {unit}')
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = \
            'attachment; filename="shopping_cart.txt"'
        return response


class FoodgramUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = FoodgramUserSerializer
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch', 'delete']
    permission_classes = (AllowAny, )

    @action(detail=False, methods=['get', ],
            permission_classes=(IsAuthenticated,)
            )
    def subscriptions(self, request):
        page = self.paginate_queryset(User.objects.filter(
            following__follower=request.user))
        serializer = SubscriptionsSerializer(
            page,
            context={'request': request},
            many=True)

        if 'recipes_limit' in request.query_params:
            limit = int(request.query_params['recipes_limit']) + 1
            for data in serializer.data:
                print(type(data))
                user = User.objects.get(username=data['username'])
                recipes = user.recipes.all().order_by('-id')[1:limit]
                serializer2 = RecipeSerializer(recipes,
                                               context={'request': request},
                                               many=True)
                data['recipes'] = serializer2.data
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', ],
            permission_classes=(IsAuthenticated,),
            )
    def subscribe(self, request, id):
        user = get_object_or_404(User, pk=id)
        serializer_subspript = SubscriptionsPostSerializer(
            data={'follower': request.user.id, 'following': id},
            context={'request': request})
        serializer_subspript.is_valid(raise_exception=True)
        serializer_subspript.save()
        serializer_user = SubscriptionsSerializer(user,
                                                  context={'request': request})
        if 'recipes_limit' in request.query_params:
            limit = int(request.query_params['recipes_limit']) + 1
            recipes = user.recipes.all().order_by('-id')[1:limit]
            serializer_recipe = RecipeSerializer(recipes,
                                                 context={'request': request},
                                                 many=True)
            serializer_user.data['recipes'].clear()
            serializer_user.data['recipes'].extend(
                list(serializer_recipe.data))
        return Response(serializer_user.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if not Subscriptions.objects.filter(follower__id=request.user.id,
                                            following=author).exists():
            return Response({'errors': 'Вы не подписаны на этого автора!'},
                            status=status.HTTP_400_BAD_REQUEST)
        Subscriptions.objects.filter(follower__id=request.user.id,
                                     following=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get', ],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = FoodgramUserSerializer(
            get_object_or_404(User, username=request.user),
            context={'request': request})
        return Response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilter
