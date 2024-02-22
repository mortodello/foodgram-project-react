from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from recipes.views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                           TagViewSet, FollowViewSet, FavoritesViewSet, FavoriteView)
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet)
router.register(r'users', CustomUserViewSet)
router.register(r'subscriptions', FollowViewSet, basename='following')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),  # Работа с пользователями
    path('api/auth/', include('djoser.urls.authtoken')),  # Работа с токенами
    path('api/recipes/<int:id>/favorite/', FavoriteView.as_view(), name='favorite'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
