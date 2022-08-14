from django.urls import include, path
from rest_framework import routers

from .views import (CustomUserViewSet, IngredientViweSet, RecipeViweSet,
                    TagViweSet)

router = routers.DefaultRouter()
router.register(r"tags", TagViweSet, basename="tags")
router.register(r"recipes", RecipeViweSet, basename="recipes")
router.register(r"ingredients", IngredientViweSet, basename="ingredients")
router.register(r"users", CustomUserViewSet, basename="users")


urlpatterns = [
    path("", include(router.urls)),
    path("", include("djoser.urls")),
    path("auth/", include("djoser.urls.authtoken")),
]
