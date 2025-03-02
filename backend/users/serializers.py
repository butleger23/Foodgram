from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from recipes.models import Recipe
from users.models import MAX_USERNAME_LENGTH


User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        max_length=MAX_USERNAME_LENGTH,
        validators=[
            UnicodeUsernameValidator(),
            UniqueValidator(User.objects.all()),
        ],
    )
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def validate(self, attrs):
        if 'avatar' not in attrs:
            raise serializers.ValidationError(
                {'avatar': 'This field is required.'}
            )
        return attrs


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

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
            'password',
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


class UserSubscriptionSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()
    recipes = SimpleRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(
        source='recipes.count', read_only=True
    )

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
            'recipes',
            'recipes_count',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        recipes_limit = self.context.get('recipes_limit', None)
        if recipes_limit is not None and 'recipes' in representation:
            representation['recipes'] = representation['recipes'][
                : int(recipes_limit)
            ]
        return representation

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.subscriptions.filter(id=obj.id).exists()
        return False
