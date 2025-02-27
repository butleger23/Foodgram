from django.http import HttpResponseNotFound
from rest_framework import serializers, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from users.serializers import UserSerializer
from ingredients.models import Ingredient
from tags.models import Tag
from tags.serializers import TagSerializer
from django.shortcuts import get_object_or_404
from django.http.response import Http404, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist

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
    image = Base64ImageField(required=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredient', read_only=True, many=True
    )
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()


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
            'is_favorited',
            'is_in_shopping_cart',
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request.user.is_anonymous:
            return request.user.favorites_list.filter(id=obj.id).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request.user.is_anonymous:
            return request.user.shopping_cart.filter(id=obj.id).exists()
        return False

    def validate_tags_and_ingredients(self, tags_ids, ingredients):
        if len(tags_ids) != len(set(tags_ids)):
            raise serializers.ValidationError({'tags': 'Тэги не должны повторяться'})

        tags = Tag.objects.filter(id__in=tags_ids)
        if not tags:
            raise serializers.ValidationError({'tags': 'Тэги с данными id не существуют'})

        if not ingredients:
            raise serializers.ValidationError({'ingredients': 'Для создания рецепта требуются ингредиенты'})

        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({'ingredients': 'Ингредиенты не должны повторяться'})

        for ingredient in ingredients:
            try:
                Ingredient.objects.get(pk=ingredient['id'])
            except ObjectDoesNotExist:
                raise serializers.ValidationError({'ingredients': 'Данного ингредиента не существует'})

            if ingredient['amount'] <= 0:
                raise serializers.ValidationError({'ingredients': 'Количество ингредиента должно быть больше 0'})

        return tags, ingredients

    def create_or_update_recipe(self, instance, validated_data):
        image = validated_data.get('image', [])
        if not image:
            raise serializers.ValidationError({'image': 'Для создания рецепта требуется добавить изображение'})

        tags_ids = self.initial_data.get('tags', [])
        ingredients = self.initial_data.get('ingredients', [])

        tags, ingredients = self.validate_tags_and_ingredients(tags_ids, ingredients)

        if instance is None:
            instance = Recipe.objects.create(**validated_data)
        else:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

        instance.tags.clear()
        instance.tags.add(*tags)

        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient in ingredients:
            ingredient_object = Ingredient.objects.get(pk=ingredient['id'])
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_object,
                amount=ingredient['amount'],
            )

        return instance

    def create(self, validated_data):
        return self.create_or_update_recipe(None, validated_data)

    def update(self, instance, validated_data):
        return self.create_or_update_recipe(instance, validated_data)
