from django.db import models
from django.contrib.auth import get_user_model

from ingredients.models import Ingredient
from tags.models import Tag

User = get_user_model()

RECIPE_MAX_LENGTH = 50


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    users_who_favourited_this = models.ManyToManyField(
        User, related_name='recipes', blank=True
    )  # not sure how that'll work
    users_who_put_this_in_shopping_list = models.ManyToManyField(
        User, related_name='recipes+', blank=True
    )
    name = models.CharField(max_length=RECIPE_MAX_LENGTH)
    image = models.ImageField('Фото', upload_to='recipes_images')
    tags = models.ManyToManyField(Tag, related_name='recipes')
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient', related_name='recipes')
    text = models.TextField('Описание')
    cooking_time = models.SmallIntegerField('Время приготовления в минутах')

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredient')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name='recipe_ingredient')
    amount = models.IntegerField()