from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Ingredient, Recipe, Tag

User = get_user_model()


admin.site.register(User)
admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(Ingredient)
