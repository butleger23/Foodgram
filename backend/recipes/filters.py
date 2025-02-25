from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='filter_is_in_shopping_cart')
    author = filters.NumberFilter(field_name='author__id')
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

    def filter_is_favorited(self, queryset, name, value):
        if value == 1:
            return queryset.filter(users_who_favorited_this__id=self.request.user.id)
        elif value == 0:
            return queryset.exclude(users_who_favorited_this__id=self.request.user.id)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == 1:
            return queryset.filter(users_who_put_this_in_shopping_cart__id=self.request.user.id)
        elif value == 0:
            return queryset.exclude(users_who_put_this_in_shopping_cart__id=self.request.user.id)
        return queryset