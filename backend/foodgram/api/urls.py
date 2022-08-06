from django.urls import include, path
from rest_framework import routers

from .views import (TagViweSet,
                    RecipeViweSet,
                    IngredientViweSet,
                    FavoriteViweSet)

router = routers.DefaultRouter()
router_recipe = routers.DefaultRouter()
router.register(r'tags', TagViweSet)
router.register(r'recipes', RecipeViweSet)
router_recipe.register(
    r'(?P<name_id>\d+)/favorite', FavoriteViweSet, basename='favorite')
router.register(r'ingredients', IngredientViweSet)
# router.register(r'users/?P<username_id>\d+)/subscribe/', ViweSet)


urlpatterns = [
    path('', include(router.urls)),
    path('recipes/', include(router_recipe.urls)),
]
