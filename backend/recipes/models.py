from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()

RECIPE_MAX_LENGTH = 256
SHORT_LINK_LENGTH = 5
MINIMUM_COOKING_TIME = MINIMUM_INGREDIENT_AMOUNT = 1


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    users_who_favorited_this = models.ManyToManyField(
        User, related_name='favorites_list', blank=True
    )
    users_who_put_this_in_shopping_cart = models.ManyToManyField(
        User, related_name='shopping_cart', blank=True
    )
    name = models.CharField(max_length=RECIPE_MAX_LENGTH)
    image = models.ImageField('Фото', upload_to='recipes_images')
    tags = models.ManyToManyField(Tag, related_name='recipes')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes_ingredients',
    )
    text = models.TextField('Описание')
    cooking_time = models.SmallIntegerField(
        'Время приготовления в минутах',
        validators=[MinValueValidator(MINIMUM_COOKING_TIME)],
    )
    short_link = models.CharField(
        max_length=SHORT_LINK_LENGTH, unique=True, null=True
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredient'
    )
    amount = models.SmallIntegerField(
        'Количество', validators=[MinValueValidator(MINIMUM_INGREDIENT_AMOUNT)]
    )
