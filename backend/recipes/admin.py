from django.contrib import admin
from .models import Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author__username')
    search_fields = ('author__username', 'name')
    list_filter = ('tags__slug',)
    readonly_fields = ('favorites_count',)
    inlines = [RecipeIngredientInline]

    def favorites_count(self, obj):
        return obj.users_who_favorited_this.count()
    favorites_count.short_description = 'Favorites count'


admin.site.register(Recipe, RecipeAdmin)
