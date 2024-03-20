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
from users.models import CustomUser

from .filters import IngredientFilter, RecipeFilter
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Subscriptions, Tag)
from .permissions import IsAdminAuthorOrReadOnly
from .serializers import (CustomUserSerializer, IngredientSerializer,
                          RecipeSerializer, SubscriptionsSerializer,
                          TagSerializer)

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

    @action(detail=True, methods=['get', 'post', 'delete'],
            permission_classes=[IsAuthenticated, ])
    def favorite(self, request, pk):
        Favorite.objects.create(user=self.request.user,
                                recipes=get_object_or_404(Recipe, id=pk))
        serializer = RecipeSerializer(Recipe.objects.get(id=pk),
                                      context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated, ])
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            serializer = RecipeSerializer(
                data={'user': request.user.id, 'recipe': recipe.id, },
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            error_message = 'У вас нет этого рецепта в списке покупок'
            if not ShoppingCart.objects.filter(user=request.user,
                                               recipe=recipe).exists():
                return Response({'errors': error_message},
                                status=status.HTTP_400_BAD_REQUEST)
            ShoppingCart.objects.filter(user=request.user,
                                        recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated, ])
    def download_shopping_cart(self, request):
        ingredients = IngredientRecipe.objects.filter(
            recipe__carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
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


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'patch']
    permission_classes = (AllowAny, )

    @action(detail=False, methods=['get',],
            permission_classes=(IsAuthenticated,),
            pagination_class=LimitOffsetPagination
            )
    def subscriptions(self, request):
        user = User.objects.get(username=self.request.user)
        users = user.followers.all()
        serializer = SubscriptionsSerializer(
            [User.objects.get(pk=user.following.id) for user in users],
            context={'request': request},
            many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post', 'delete'],
            permission_classes=(IsAuthenticated,),
            )
    def subscribe(self, request, id):
        Subscriptions.objects.create(follower=self.request.user,
                                     following=User.objects.get(pk=id))
        serializer = SubscriptionsSerializer(User.objects.get(pk=id),
                                             context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get',],
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = CustomUserSerializer(
            get_object_or_404(CustomUser, username=request.user),
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
