from django_filters import rest_framework as filters
from django.db.models import Q

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
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        if value:
            return queryset.filter(
                users_who_favorited_this__id=self.request.user.id
            )
        else:
            return queryset.exclude(
                users_who_favorited_this__id=self.request.user.id
            )

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                users_who_put_this_in_shopping_cart__id=self.request.user.id
            )
        else:
            return queryset.exclude(
                users_who_put_this_in_shopping_cart__id=self.request.user.id
            )

    def filter_tags(self, queryset, name, value):
        tags = self.request.query_params.getlist('tags')
        q_objects = Q()
        for tag in tags:
            q_objects |= Q(tags__slug__iexact=tag.strip())
        return queryset.filter(q_objects).distinct()
