from django.http import HttpResponse
from django.db.models import Sum
import csv
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from users.models import Subscribe, User

from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    CustomUserSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    PasswordSerilizer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    ShoppingCartSerializer,
    SubscribeSerializer,
    TagSerializer,
)
from .permissions import IsAdminOrReadOnly


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=False, methods=["POST"], permission_classes=(IsAuthenticated,)
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
        detail=False, methods=["GET"], permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(follower__user=request.user)
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
        recipe_id = int(self.kwargs['recipe_id'])
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        follow = Favorite.objects.filter(user=user, recipe=recipe)
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == "POST":
            if follow.exists():
                data = {"errors": ("Вы уже добавили этот рецепт в избранное")}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            favorite = Favorite.objects.create(recipe=recipe)
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
        recipe_id = int(self.kwargs['recipe_id'])
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == "POST":
            if shopping_cart.exists():
                data = {
                    "errors": ("Вы уже добавили этот рецепт список покупок")
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            cart = ShoppingCart.objects.create(recipe=recipe)
            serializer = ShoppingCartSerializer(cart.recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            if not shopping_cart.exists():
                data = {"errors": ("Такого рецепта нет в списке покупок")}
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            shopping_cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=["GET"], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        # user = self.request.user
        # shoping_cart = user.purchases.all()
        # recipe_ingredients = {}
        # for i in shoping_cart:
        #     recipe = i.recipe
        #     ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        #     for ingredient in ingredients:
        #         amount = ingredient.amount
        #         name = ingredient.ingredient.name
        #         measurement_unit = ingredient.ingredient.measurement_unit
        #         if name not in recipe_ingredients:
        #             recipe_ingredients[name] = {
        #                 "amount": amount,
        #                 "measurement_unit": measurement_unit,
        #             }
        #         else:
        #             recipe_ingredients[name]["amount"] = (
        #                 recipe_ingredients[name]["amount"] + amount
        #             )
        # shopping_list = []
        # for i in recipe_ingredients:
        #     shopping_list.append(
        #         f'{i} - {recipe_ingredients[i]["amount"]} '
        #         f'{recipe_ingredients[i]["measurement_unit"]}'
        #     )
        # response = HttpResponse(shopping_list, "Content-Type: text/plain")
        # response["Content-Disposition"] = 'attachment; filename="shoplist.txt"'
        # return response
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(ingredient_amount=Sum('amount')).values_list(
            'ingredients__name', 'ingredients__measurement_unit',
            'ingredients_amount')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = ('attachment;'
                                           'filename="Shoppingcart.csv"')
        response.write(u'\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        for item in list(ingredients):
            writer.writerow(item)
        return response
