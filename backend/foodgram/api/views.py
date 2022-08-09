# from django.contrib.auth.tokens import default_token_generator
# from django.core.mail import send_mail
# from django.db.models import Avg
from multiprocessing import context
from django.shortcuts import get_object_or_404
# from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
#from psycopg2 import DatabaseError
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from users.models import User, Subscribe
from recipes.models import Recipe, Tag, Ingredient, Favorite
from .serializers import (CustomUserSerializer,
                          PasswordSerilizer,
                          SubscribeSerializer,
                          RecipeSerializer,
                          IngredientSerializer,
                          TagSerializer,
                          FavoriteSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(detail=False,
            methods=['POST'],
            permission_classes=(IsAuthenticated, ))
    def set_password(self, request, pk=None):
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = PasswordSerilizer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user.set_password(serializer.data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['GET'],
            permission_classes=(IsAuthenticated, ))
    def subscriptions(self, request):
        queryset = User.objects.filter(follower__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated, ))
    def subscribe(self, request, id):
        user = self.request.user
        author = get_object_or_404(User, id=id)
        follow = Subscribe.objects.filter(
            user=user,
            author=author
            )
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            if user == author:
                data = {
                    'errors':
                        ('Вы пытаетесь подписаться на самого себя')
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            if follow.exists():
                data = {
                    'errors':
                        ('Вы уже подписаны на этого автора')
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            Subscribe.objects.create(user=user, author=author)
            serializer = SubscribeSerializer(author,
                                             context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not follow.exists():
                data = {
                    'errors':
                        ('Вы не подписаны на этого автора')
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViweSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = TagSerializer


class IngredientViweSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = IngredientSerializer


class RecipeViweSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=(IsAuthenticated, ))
    def favorite(self, request, id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=id)
        follow = Favorite.objects.filter(
            user=user,
            recipe=recipe
            )
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if request.method == 'POST':
            if follow.exists():
                data = {
                    'errors':
                        ('Вы уже добавили этот рецепт в избранное')
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            favorite = Favorite.objects.create(recipe=recipe)
            serializer = FavoriteSerializer(favorite.recipe)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not follow.exists():
                data = {
                    'errors':
                        ('Такого рецепта нет в избранных')
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
