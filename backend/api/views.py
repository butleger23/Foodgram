from io import BytesIO

from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from ingredients.models import Ingredient
from recipes.models import (
    FavoritesListRecipe,
    Recipe,
    RecipeIngredient,
    ShoppingCartRecipe,
)
from tags.models import Tag
from users.models import Subscriptions
from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPaginationClass
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CreateSubscriptionSerializer,
    DisplaySubscriptionSerializer,
    FavoritesListRecipeSerializer,
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartRecipeSerializer,
    TagSerializer,
    UserAvatarSerializer,
)


User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class UserViewSet(DjoserUserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPaginationClass

    def get_permissions(self):
        if self.action in ('list', 'create', 'retrieve', 'get_token'):
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def me(self, request):
        return super().me(request)

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        serializer_class=UserAvatarSerializer,
    )
    def avatar(self, request):
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete()
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, serializer_class=DisplaySubscriptionSerializer)
    def subscriptions(self, request):
        recipes_limit = request.query_params.get('recipes_limit', None)
        subscriptions = Subscriptions.objects.filter(
            subscriber=request.user
        ).select_related('subscribed_to')
        page = self.paginate_queryset(subscriptions)

        serializer = DisplaySubscriptionSerializer(
            [sub.subscribed_to for sub in page],
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit},
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, id=None):
        recipes_limit = request.query_params.get('recipes_limit', None)
        subscriber = request.user
        subscribed_to = get_object_or_404(User, pk=id)

        subscription_data = {
            'subscriber': subscriber.id,
            'subscribed_to': subscribed_to.id,
        }
        serializer = CreateSubscriptionSerializer(
            data=subscription_data,
            context={
                'request': request,
                'recipes_limit': recipes_limit,
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        subscriber = request.user
        subscribed_to = get_object_or_404(User, pk=id)

        deleted_count, _ = Subscriptions.objects.filter(
            subscriber=subscriber, subscribed_to=subscribed_to
        ).delete()

        if not deleted_count:
            return Response(
                {'error': 'You are not subscribed to this user.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginationClass
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False)
    def download_shopping_cart(self, request):
        pdfmetrics.registerFont(
            TTFont('Roboto-Black', 'static/Roboto-Black.ttf')
        )

        user = request.user
        print(0)
        shopping_list_result = (
            RecipeIngredient.objects.filter(recipe__shopping_cart__user=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )
        print(1)

        shopping_list_dict = {
            item['ingredient__name']: {
                'amount': item['total_amount'],
                'measurement_unit': item['ingredient__measurement_unit'],
            }
            for item in shopping_list_result
        }
        print(2)
        if not shopping_list_dict:
            return HttpResponse('Your shopping cart is empty.', status=400)

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont('Roboto-Black', 12)
        pdf.drawString(72, 750, 'Shopping List')

        y = 730
        for ingredient, details in shopping_list_dict.items():
            pdf.drawString(
                72,
                y,
                f'{ingredient}: {details["amount"]} {details["measurement_unit"]}',
            )
            y -= 20
            if y < 50:
                pdf.showPage()
                y = 750

        pdf.save()
        buffer.seek(0)

        response = FileResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.pdf"'
        )
        return response

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = ShoppingCartRecipeSerializer(
            data={'recipe': recipe.id}, context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        deleted_count, _ = ShoppingCartRecipe.objects.filter(
            user=user, recipe=recipe
        ).delete()

        if not deleted_count:
            return Response(
                {
                    'error': 'Рецепт, который вы пытаетесь удалить, '
                    'не находится в списке покупок.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoritesListRecipeSerializer(
            data={'recipe': recipe.id}, context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_from_favorite_list(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        deleted_count, _ = FavoritesListRecipe.objects.filter(
            user=user, recipe=recipe
        ).delete()

        if not deleted_count:
            return Response(
                {
                    'error': 'Рецепт, который вы пытаетесь удалить, '
                    'не находится в списке избранного.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = recipe.short_link

        return Response(
            {'short-link': request.build_absolute_uri(f'/s/{short_link}')}
        )


def redirect_to_recipe(request, short_link):
    recipe = get_object_or_404(Recipe, short_link=short_link)
    redirect_url = f'/recipes/{recipe.id}/'
    return redirect(redirect_url)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
