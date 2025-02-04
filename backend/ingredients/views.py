from tags.views import GetViewSet

from .serializers import IngredientSerializer
from .models import Ingredient


class IngredientViewSet(GetViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
