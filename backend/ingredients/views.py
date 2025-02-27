from tags.views import GetViewSet

from .serializers import IngredientSerializer
from .models import Ingredient
from django_filters.rest_framework import DjangoFilterBackend


class IngredientViewSet(GetViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
