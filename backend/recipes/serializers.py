from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField

from tags.serializers import TagSerializer
from ingredients.serializers import IngredientSerializer
# from tags.models import Tag

from .models import Recipe

User = get_user_model()



class RecipeSerializer(serializers.ModelSerializer):
    # tags = serializers.SlugRelatedField(slug_field='slug', many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    ingredients = IngredientSerializer(read_only=True, many=True)
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = '__all__'
        # read_only_fields = ['author']

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     representation['tags'] = TagSerializer(
    #         data=instance.tags.all(), many=True
    #     )
    #     return representation

    # def to_internal_value(self, data):
    #     return super().to_internal_value(data)