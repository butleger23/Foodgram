from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ingredients.views import IngredientViewSet
from tags.views import TagViewSet
from users.views import UserViewSet
from recipes.views import RecipeViewSet



router = DefaultRouter()
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('tags', TagViewSet, basename='tags')
router.register('users', UserViewSet, basename='users')
# router.register(r'users/(?P<user_id>\d+)/subscribe', SubscriptionViewSet, basename='subscription')


urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
