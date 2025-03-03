import random
import string

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from ingredients.models import Ingredient
from tags.models import Tag


User = get_user_model()

RECIPE_MAX_LENGTH = 256
SHORT_LINK_LENGTH = 5
MINIMUM_COOKING_TIME = MINIMUM_INGREDIENT_AMOUNT = 1
MAXIMUM_COOKING_TIME = MAXIMUM_INGREDIENT_AMOUNT = 32000


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
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
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления в минутах',
        validators=[
            MinValueValidator(
                MINIMUM_COOKING_TIME, 'Время готовки не может быть меньше 1'
            ),
            MaxValueValidator(
                MAXIMUM_COOKING_TIME,
                'Время готовки не может быть больше 32000',
            ),
        ],
    )
    short_link = models.CharField(
        max_length=SHORT_LINK_LENGTH, unique=True, null=True, blank=True
    )
    created = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-created',)

    def __str__(self):
        return self.name

    def generate_short_link(self):
        while True:
            short_link = ''.join(
                random.choices(
                    string.ascii_lowercase + string.digits,
                    k=SHORT_LINK_LENGTH,
                )
            )
            if not Recipe.objects.filter(short_link=short_link).exists():
                return short_link

    def save(self, *args, **kwargs):
        if not self.short_link:
            self.short_link = self.generate_short_link()
        super().save(*args, **kwargs)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_ingredient'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                MINIMUM_INGREDIENT_AMOUNT,
                'Количество ингредиента не может быть меньше 1',
            ),
            MaxValueValidator(
                MAXIMUM_INGREDIENT_AMOUNT,
                'Количество ингредиента не может быть больше 32000',
            ),
        ],
    )


class ShoppingCartRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shopping_cart'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_in_shopping_cart',
            )
        ]


class FavoritesListRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='favorites_list'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorites_list'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_in_favorites_list',
            )
        ]
