from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from users.serializers import UserSerializer
from ingredients.models import Ingredient
from tags.models import Tag
from tags.serializers import TagSerializer

from .models import Recipe, RecipeIngredient

User = get_user_model()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')



class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredient', read_only=True, many=True
    )
    author = UserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        ]

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

    def update(self, instance, validated_data):
        tags_ids = self.initial_data.get('tags', [])
        tags = Tag.objects.filter(id__in=tags_ids)

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.save()

        RecipeIngredient.objects.filter(recipe=instance).delete()
        ingredients = self.initial_data.get('ingredients', [])

        for ingredient in ingredients:
            ingredient_object = Ingredient.objects.get(pk=ingredient['id'])
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_object,
                amount=ingredient['amount'],
            )

        instance.tags.set(tags)
        return instance
