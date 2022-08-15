from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Favorite, Ingredient, Recipe, RecipeIngredient, Tag
from rest_framework import serializers
from users.models import User


class PasswordSerilizer(serializers.ModelSerializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class SubscribeRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)

    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.follower.filter(user=request.user, author=obj).exists()


class SubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )
        model = User

    def get_recipes(self, obj):
        recipe_limit = self.context["request"].query_params.get(
            "recipes_limit"
        )
        recipes = obj.recipes.all()
        if recipe_limit is None:
            recipes_serializer = SubscribeRecipeSerializer(recipes, many=True)
        else:
            recipe_limit = int(recipe_limit)
            recipes_serializer = SubscribeRecipeSerializer(
                recipes[:recipe_limit],
                many=True
            )
        return recipes_serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "password",
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "color", "slug")
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "measurement_unit")
        model = Ingredient


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        fields = ("id", "name", "measurement_unit", "amount")
        model = RecipeIngredient


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        fields = ("id", "amount")
        model = Ingredient


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = RecipeIngredientReadSerializer(
        many=True, required=True, source="recipe"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        model = Recipe

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return Favorite.objects.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return Recipe.objects.filter(
            shopping_cart__user=user, id=obj.id
        ).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    author = serializers.HiddenField(default=CustomUserSerializer())
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField(required=False)

    class Meta:
        fields = (
            "author",
            "ingredients",
            "tags",
            "image",
            "name",
            "text",
            "cooking_time",
        )
        model = Recipe

    def validate_ingredients(self, data):
        ingredients = self.initial_data.get("ingredients")
        if ingredients == []:
            raise ValidationError("Выберете минимум 1 ингридиент!")
        for ingredient in ingredients:
            if int(ingredient["amount"]) <= 0:
                raise ValidationError("Колличество не должно быть меньше 1!")
        tags = self.initial_data.get("tags")
        if tags == []:
            raise ValidationError("Выберете минимум 1 тэг!")
        return data

    def add_ingredients(self, ingredients, recipes):
        for ingredient in ingredients:
            ingredient_id = ingredient.get("id")
            amount = ingredient["amount"]
            current_ingredient = get_object_or_404(
                Ingredient, id=ingredient_id
            )
            RecipeIngredient.objects.create(
                ingredient=current_ingredient, recipe=recipes, amount=amount
            )
        return recipes

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        recipes = Recipe.objects.create(**validated_data)
        recipes.tags.set(tags)
        return self.add_ingredients(ingredients, recipes)

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.ingredients.clear()
        return self.add_ingredients(ingredients, instance)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        tag_id_list, tag_list = representation["tags"], []
        for tag_id in tag_id_list:
            tag = get_object_or_404(Tag, id=tag_id)
            serialized_tag = OrderedDict(TagSerializer(tag).data)
            tag_list.append(serialized_tag)
        representation["tags"] = tag_list
        return representation


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("id", "name", "image", "cooking_time")
        model = Recipe
