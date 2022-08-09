from django.urls import include, path
from rest_framework import routers

from .views import (TagViweSet,
                    RecipeViweSet,
                    IngredientViweSet,
                    FavoriteViweSet,
                    CustomUserViewSet)

router = routers.DefaultRouter()
router_recipe = routers.DefaultRouter()
router.register(r'tags', TagViweSet)
router.register(r'recipes', RecipeViweSet, basename='recipes')
router_recipe.register(r'favorite', FavoriteViweSet, basename='favorite')
router.register(r'ingredients', IngredientViweSet)
router.register(r'users', CustomUserViewSet, basename='users')


urlpatterns = [
    path('', include(router.urls)),
    path('recipes/', include(router_recipe.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
