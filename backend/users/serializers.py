from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Recipe

User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'password'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request.user.is_anonymous:
            return request.user.subscriptions.filter(id=obj.id).exists()
        return False


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'password'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request.user.is_anonymous:
            return request.user.subscriptions.filter(id=obj.id).exists()
        return False


class SimpleRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()
    recipes = SimpleRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.IntegerField(source='recipes.count', read_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
            'recipes',
            'recipes_count',
        ]


    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return request.user.subscriptions.filter(id=obj.id).exists()


# class SubscriptionSerializer(serializers.ModelSerializer):
#     user = serializers.SlugRelatedField(
#         read_only=True,
#         slug_field='username',
#         default=serializers.CurrentUserDefault(),
#     )
#     subscribing = serializers.SlugRelatedField(
#         # queryset=User.objects.all(),
#         read_only=True,
#         slug_field='username',
#         default=User.objects.first(),
#     )

#     class Meta:
#         fields = ('user', 'subscribing')
#         model = Subscription
#         validators = [
#             UniqueTogetherValidator(
#                 queryset=Subscription.objects.all(),
#                 fields=['user', 'subscribing'],
#                 message='Cannot subscribe to the same person twice',
#             )
#         ]

#     def validate_subscribing(self, subscribing):
#         if subscribing == self.context['request'].user:
#             raise serializers.ValidationError(
#                 'Choose a different person to subscribe to: cannot subscribe to yourself'
#             )
#         return subscribing
