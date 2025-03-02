from django.db import models
from django.db.models import UniqueConstraint


MAX_INGREDIENT_LENGTH = 128
MAX_MEASUREMENT_UNIT_LENGTH = 64


class Ingredient(models.Model):
    name = models.CharField('Ингредиент', max_length=MAX_INGREDIENT_LENGTH)
    measurement_unit = models.CharField(
        'Единица измерения', max_length=MAX_MEASUREMENT_UNIT_LENGTH
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)
        constraints = [
            UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit',
            )
        ]

    def __str__(self):
        return self.name
