from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from ingredients.models import Ingredient
from tags.models import Tag
from tags.serializers import TagSerializer
from ingredients.serializers import IngredientSerializer

from .models import Recipe, RecipeIngredient

User = get_user_model()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(source='recipe_ingredient', read_only=True, many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def create(self, validated_data):
        tags_ids = self.initial_data.get('tags', [])
        tags = Tag.objects.filter(id__in=tags_ids)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.add(*tags)

        ingredients = self.initial_data.get('ingredients', [])

        for ingredient in ingredients:
            ingredient_object = Ingredient.objects.get(pk=ingredient['id'])
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_object,
                amount=ingredient['amount'],
            )

        return recipe

    # def update(self, instance, validated_data):
    #     # Extract tag IDs from validated data
    #     tags = validated_data.pop('tags', [])
    #     # Update the recipe fields
    #     instance.title = validated_data.get('title', instance.title)
    #     instance.save()
    #     # Update the associated tags
    #     instance.tags.set(tags)
    #     return instance
