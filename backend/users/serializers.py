from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework.validators import UniqueTogetherValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()
    username = serializers.CharField(required=True)


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
        ]

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request.user.is_anonymous:
            return request.user.subscriptions.filter(id=obj.id).exists()
        return False


class UserSubscriptionSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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

    def get_recipes(self, obj):

        return 1

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return request.user.subscriptions.filter(id=obj.id).exists()

    def get_recipes_count(self, obj):
        return 1


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
