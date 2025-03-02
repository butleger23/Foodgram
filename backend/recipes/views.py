import random
import string
from io import BytesIO

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404, redirect
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import CustomPaginationClass
from recipes.filters import RecipeFilter
from recipes.permissions import IsAuthorOrReadOnly
from users.serializers import SimpleRecipeSerializer
from .models import (
    SHORT_LINK_LENGTH,
    FavoritesListRecipe,
    Recipe,
    RecipeIngredient,
    ShoppingCartRecipe,
)
from .serializers import (
    FavoritesListRecipeSerializer,
    RecipeReadSerializer,
    RecipeWriteSerializer,
    ShoppingCartRecipeSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPaginationClass
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly]

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

        shopping_list_result = (
            RecipeIngredient.objects.filter(recipe__shopping_cart__user=user)
            .values('ingredient__name')
            .annotate(total_amount=Sum('amount'))
        )

        shopping_list_dict = {
            item['ingredient__name']: item['total_amount']
            for item in shopping_list_result
        }

        if not shopping_list_dict:
            return HttpResponse('Your shopping cart is empty.', status=400)

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=letter)

        pdf.setFont('Roboto-Black', 12)
        pdf.drawString(72, 750, 'Shopping List')

        y = 730
        for ingredient, amount in shopping_list_dict.items():
            pdf.drawString(72, y, f'{ingredient}: {amount}')
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

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def delete_from_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        deleted_count, _ = ShoppingCartRecipe.objects.filter(
            user=user, recipe=recipe
        ).delete()

        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {
                    'error': 'Рецепт, который вы пытаетесь удалить, '
                    'не находится в списке покупок.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = FavoritesListRecipeSerializer(
            data={'recipe': recipe.id}, context={'request': request}
        )

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def delete_from_favorite_list(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        deleted_count, _ = FavoritesListRecipe.objects.filter(
            user=user, recipe=recipe
        ).delete()

        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {
                    'error': 'Рецепт, который вы пытаетесь удалить, '
                    'не находится в списке избранного.'
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = recipe.short_link

        return Response(
            {'short-link': request.build_absolute_uri(f'/s/{short_link}')}
        )


def redirect_to_recipe(request, short_link):
    recipe = get_object_or_404(Recipe, short_link=short_link)
    redirect_url = f'/api/recipes/{recipe.id}/'
    return redirect(redirect_url)
