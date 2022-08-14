from django.db import models
from users.models import User
from django.core.validators import MinValueValidator


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name="Наименование ингредиента",
        max_length=200
    )
    measurement_unit = models.CharField(
        verbose_name="Единица измерения",
        max_length=200
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    name = models.CharField(
        verbose_name="Название",
        unique=True,
        max_length=256
    )
    color = models.CharField(
        verbose_name="Цвет в HEX",
        unique=True,
        max_length=256
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name="Уникальный слаг"
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes"
    )
    name = models.CharField(
        verbose_name="Наименование рецепта",
        max_length=256,
        unique=True
    )
    image = models.ImageField(
        verbose_name="Картинка",
        upload_to="recipes/images/",
        blank=True,
        null=True,
    )
    text = models.TextField(verbose_name="Описание рецепта")
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингридиент",
        through="RecipeIngredient",
    )
    tags = models.ManyToManyField(
        Tag, verbose_name=("Тег"),
        related_name="recipes"
    )
    cooking_time = models.IntegerField(
        verbose_name="Время приготовления (в минутах)",
        validators=[MinValueValidator(1)],
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата публикации",
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredient"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe"
    )
    amount = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        unique_together = [["ingredient", "recipe"]]


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites"
    )


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart"
    )
