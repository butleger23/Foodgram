from django.contrib import admin
from django.contrib.auth import get_user_model

from backend.recipes.models import Ingredient, Recipe, Tag


User = get_user_model()

class UserAdmin(admin.ModelAdmin):
    search_fields = ('email', 'username')


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author__username')
    search_fields = ('author__username', 'name')
    list_filter = ('tags__slug',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)

admin.site.register(User, UserAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(Ingredient)
