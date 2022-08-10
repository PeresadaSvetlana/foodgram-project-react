import django_filters as filters
from recipes.models import Recipe, Ingredient
from users.models import User


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class IngredientFilter(filters.FilterSet):
    name=filters.CharFilter(field_name='name',
                            lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
