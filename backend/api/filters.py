from django.db.models import Q
from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.CharFilter(method='filter_tags')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(
                favorites_list__user=self.request.user
            )
        else:
            return queryset.exclude(
                favorites_list__user=self.request.user
            )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                shopping_cart__user=self.request.user
            )
        else:
            return queryset.exclude(
                shopping_cart__user=self.request.user
            )

    def filter_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags')
        q_objects = Q()
        for tag in tags:
            q_objects |= Q(tags__slug__iexact=tag.strip())
        return queryset.filter(q_objects).distinct()
