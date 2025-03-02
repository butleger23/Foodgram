from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ingredients.models import Ingredient
from tags.models import Tag
from tags.serializers import TagSerializer
from users.serializers import UserSerializer
from .models import (
    FavoritesListRecipe,
    Recipe,
    RecipeIngredient,
    ShoppingCartRecipe,
)


User = get_user_model()


class Simple2RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class ShoppingCartRecipeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCartRecipe
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCartRecipe.objects.all(),
                fields=['user', 'recipe']
            )
        ]

    def validate_recipe(self, value):
        user = self.context['request'].user
        if ShoppingCartRecipe.objects.filter(user=user, recipe=value).exists():
            raise serializers.ValidationError(
                'Рецепт, который вы пытаетесь добавить, уже находится в списке покупок.'
            )
        return value

    def to_representation(self, instance):
        return Simple2RecipeSerializer(instance.recipe).data


class FavoritesListRecipeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = FavoritesListRecipe
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=FavoritesListRecipe.objects.all(),
                fields=['user', 'recipe']
            )
        ]

    def validate_recipe(self, value):
        user = self.context['request'].user
        if FavoritesListRecipe.objects.filter(user=user, recipe=value).exists():
            raise serializers.ValidationError(
                'Рецепт, который вы пытаетесь добавить, уже находится в списке избранного.'
            )
        return value

    def to_representation(self, instance):
        return Simple2RecipeSerializer(instance.recipe).data


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
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
        return bool(
            (request := self.context.get('request'))
            and request.user.is_authenticated
            and FavoritesListRecipe.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        return bool(
            (request := self.context.get('request'))
            and request.user.is_authenticated
            and ShoppingCartRecipe.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, required=True
    )
    ingredients = RecipeIngredientWriteSerializer(many=True, required=True)

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
        read_only_fields = ['author']

    def validate(self, data):
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                {'ingredients': 'Для создания рецепта требуются ингредиенты'}
            )
        if 'tags' not in data:
            raise serializers.ValidationError(
                {'tags': 'Для создания рецепта требуются теги'}
            )
        return data

    def validate_tags(self, tags):
        if tags is None:
            raise serializers.ValidationError(
                {'tags': 'Поле tags обязательно для заполнения'}
            )

        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Для создания рецепта требуются теги'}
            )

        tag_ids = [tag.id for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны повторяться'}
            )

        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Для создания рецепта требуются ингредиенты'}
            )

        ingredient_ids = [ingredient['id'].id for ingredient in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться'}
            )

        return ingredients

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError(
                {
                    'image': 'Для создания рецепта требуется добавить изображение'
                }
            )
        return image

    def create_or_update_recipe(self, instance, validated_data):
        tags = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])

        if instance is None:
            instance = Recipe.objects.create(**validated_data)
        else:
            instance = super().update(instance, validated_data)

        instance.tags.set(tags)

        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount'],
            )

        return instance

    def create(self, validated_data):
        return self.create_or_update_recipe(None, validated_data)

    def update(self, instance, validated_data):
        return self.create_or_update_recipe(instance, validated_data)

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance, context=self.context
        ).to_representation(instance)
