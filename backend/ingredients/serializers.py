from rest_framework import serializers

from recipes.models import Recipe, RecipeIngredient


from .models import Ingredient


# class DynamicFieldsMixin:
#     def __init__(self, *args, **kwargs):
#         fields = kwargs.pop('fields', None)
#         super().__init__(*args, **kwargs)

#         if fields is not None:
#             allowed = set(fields)
#             existing = set(self.fields)
#             for field_name in existing - allowed:
#                 self.fields.pop(field_name)


class IngredientSerializer(serializers.ModelSerializer):
    amount = serializers.SerializerMethodField(required=False)

    def get_amount(self, obj):
        print(obj.id)
        print(RecipeIngredient.objects.filter(pk=obj.id).last().ingredient)
        return 2

    class Meta:
        model = Ingredient
        fields = '__all__'
