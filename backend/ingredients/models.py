from django.db import models

MAX_INGREDIENT_LENGTH = 20
MAX_MEASUREMENT_UNIT_LENGTH = 5


class Ingredient(models.Model):
    name = models.CharField('Ингредиент', max_length=MAX_INGREDIENT_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MAX_MEASUREMENT_UNIT_LENGTH
    )

    def __str__(self):
        return self.name
