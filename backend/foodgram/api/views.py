from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Subscribe, User

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPaginator
from .permissions import IsAdminOrReadOnly
from .serializers import (CustomUserSerializer, FavoriteSerializer,
                          IngredientSerializer, PasswordSerilizer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          TagSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPaginator

    @action(
        detail=False,
        methods=["POST"],
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request, pk=None):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = PasswordSerilizer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            user.set_password(serializer.data["new_password"])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True, context={"request": request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        follow = Subscribe.objects.filter(user=user, author=author)
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == "POST":
            if user == author:
                data = {"errors": ("Вы пытаетесь подписаться на самого себя")}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            if follow.exists():
                data = {"errors": ("Вы уже подписаны на этого автора")}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            Subscribe.objects.create(user=user, author=author)
            serializer = SubscribeSerializer(
                author, context={"request": request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if not follow.exists():
                data = {"errors": ("Вы не подписаны на этого автора")}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViweSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViweSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViweSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = RecipeCreateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPaginator

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    def get_serializer_class(self):
        if self.request.method == "GET":
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, *args, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=int(kwargs["pk"]))
        follow = Favorite.objects.filter(user=user, recipe=recipe)
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == "POST":
            if follow.exists():
                data = {"errors": ("Вы уже добавили этот рецепт в избранное")}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            favorite = Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteSerializer(favorite.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if not follow.exists():
                data = {"errors": ("Такого рецепта нет в избранных")}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, *args, **kwargs):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=int(kwargs["pk"]))
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == "POST":
            if shopping_cart.exists():
                data = {
                    "errors": ("Вы уже добавили этот рецепт список покупок")
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            cart = ShoppingCart.objects.create(user=user, recipe=recipe)
            serializer = ShoppingCartSerializer(cart.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if not shopping_cart.exists():
                data = {"errors": ("Такого рецепта нет в списке покупок")}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        shoping_list = "Список покупок:\n\n"
        user = request.user
        ingredients = (
            RecipeIngredient.objects.filter(recipe__shopping_cart__user=user)
            .values(
                "ingredient__name",
                "ingredient__measurement_unit",
            )
            .annotate(total_amount=Sum("amount"))
        )
        for position, ingredient in enumerate(ingredients, start=1):
            shoping_list += (
                f'{ingredient["ingredient__name"]} '
                f'{ingredient["total_amount"]} '
                f'{ingredient["ingredient__measurement_unit"]}\n'
            )
        response = HttpResponse(shoping_list, "Content-Type: text/plain")
        response["Content-Disposition"] = 'attachment; filename="BuyList.txt"'
        return response
