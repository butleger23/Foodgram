from rest_framework import mixins, viewsets

from .models import Tag
from .serializers import TagSerializer


class GetViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    pass


class TagViewSet(GetViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
