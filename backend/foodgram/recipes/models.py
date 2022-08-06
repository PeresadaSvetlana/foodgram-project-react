from django.db import models
from users.models import User
from multiselectfield import MultiSelectField
from django.core.validators import MinLengthValidator


class Ingredient(models.Model):
    ingredient = models.CharField(
        verbose_name='Наименование ингредиента', max_length=200)
    number = models.IntegerField(
        verbose_name='Колличество')
    unit_of_measure = models.TextField(
        verbose_name='Единица измерения')

    def __str__(self):
        return self.ingredient


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        max_length=256
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Уникальный слаг')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes')
    name = models.CharField(
        verbose_name='Наименование рецепта',
        max_length=256
    )
    image = models.ImageField(
        verbose_name='Картинка',
        upload_to='recipes/',
        blank=True, null=True
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    ingredients = MultiSelectField(Ingredient)
    tags = MultiSelectField(Tag)
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[MinLengthValidator(1)])

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name
