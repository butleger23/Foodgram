from django_filters.rest_framework import DjangoFilterBackend

from tags.views import GetViewSet
from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(GetViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name']
