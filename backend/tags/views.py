from rest_framework import mixins, viewsets

from .serializers import TagSerializer

from .models import Tag


class GetViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    pass


class TagViewSet(GetViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
