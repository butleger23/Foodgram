from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ingredients.models import Ingredient
from recipes.models import (
    FavoritesListRecipe,
    Recipe,
    RecipeIngredient,
    ShoppingCartRecipe,
)
from tags.models import Tag
from users.models import Subscriptions


User = get_user_model()


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, data):
        # Check if 'ingredients' key is present in the request data
        if 'avatar' not in data:
            raise serializers.ValidationError(
                {'avatar': 'This field is required.'}
            )
        return data

    def validate_avatar(self, value):
        # Check the ingredient value
        if not value:
            raise serializers.ValidationError(
                'The avatar field cannot be empty.'
            )
        return value

class UserListSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return bool(
            (request := self.context.get('request'))
            and request.user.is_authenticated
            and request.user.subscriptions.filter(id=obj.id).exists()
        )


class SimpleRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class DisplaySubscriptionSerializer(UserListSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserListSerializer.Meta):
        fields = UserListSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        recipes = obj.recipes.all()
        recipes_limit = self.context.get('recipes_limit', None)
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except (ValueError, TypeError):
                pass
        return SimpleRecipeSerializer(recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriptions
        fields = ('subscriber', 'subscribed_to')

    def validate(self, data):
        subscriber = data.get('subscriber')
        subscribed_to = data.get('subscribed_to')

        if subscriber == subscribed_to:
            raise ValidationError('You cannot subscribe to yourself.')

        if Subscriptions.objects.filter(
            subscriber=subscriber, subscribed_to=subscribed_to
        ).exists():
            raise ValidationError('You are already subscribed to this user.')

        return data

    def to_representation(self, instance):
        display_serializer = DisplaySubscriptionSerializer(
            instance.subscribed_to,
            context=self.context,
        )
        return display_serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class Simple2RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartRecipeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCartRecipe
        fields = ['user', 'recipe']
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCartRecipe.objects.all(),
                fields=('user', 'recipe'),
            )
        ]

    def validate_recipe(self, value):
        user = self.context['request'].user
        if ShoppingCartRecipe.objects.filter(user=user, recipe=value).exists():
            raise serializers.ValidationError(
                'Рецепт, который вы пытаетесь добавить, '
                'уже находится в списке покупок.'
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
                fields=('user', 'recipe'),
            )
        ]

    def validate_recipe(self, value):
        user = self.context['request'].user
        if FavoritesListRecipe.objects.filter(
            user=user, recipe=value
        ).exists():
            raise serializers.ValidationError(
                'Рецепт, который вы пытаетесь добавить, '
                'уже находится в списке избранного.'
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
    author = UserListSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
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
        )

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
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)


    def validate(self, data):
        # Check if 'ingredients' key is present in the request data
        if 'ingredients' not in data:
            raise serializers.ValidationError(
                {'ingredients': 'Для создания рецепта требуются ингредиенты'}
            )
        # Check if 'tags' key is present in the request data
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
                    'image': (
                        'Для создания рецепта требуется добавить изображение'
                    )
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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        validators = [
            UniqueTogetherValidator(
                queryset=Ingredient.objects.all(),
                fields=('name', 'measurement_unit'),
            )
        ]
