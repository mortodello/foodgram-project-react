from rest_framework import routers

from recipes.views import (FoodgramUserViewSet, IngredientViewSet,
                           RecipeViewSet, TagViewSet)


router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet)
router.register(r'users', FoodgramUserViewSet)
