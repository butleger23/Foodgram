
# from recipes.models import Recipe


# class RecipeFilter(filters.FilterSet):
#     is_favorited = filters.BooleanFilter(field_name='is_favorited', method='filter_is_favorited')
#     is_in_shopping_cart = filters.BooleanFilter(field_name='is_in_shopping_cart', method='filter_is_in_shopping_cart')
#     author = filters.NumberFilter(field_name='author__id')
#     tags = filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')

#     class Meta:
#         model = Recipe
#         fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']

#     def filter_is_favorited(self, queryset, name, value):
#         if value:
#             return queryset.filter(favorited_by__id=self.request.user.id)
#         return queryset

#     def filter_is_in_shopping_cart(self, queryset, name, value):
#         if value:
#             return queryset.filter(shopping_cart__id=self.request.user.id)
#         return queryset