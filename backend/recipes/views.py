import random
import string
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.db import IntegrityError
from django.http import HttpResponseBadRequest
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404, redirect
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.http import FileResponse
from ingredients.models import Ingredient
from users.serializers import SimpleRecipeSerializer

from .models import SHORT_LINK_LENGTH, Recipe, RecipeIngredient
from .serializers import RecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=False)
    def download_shopping_cart(self, request):
        def generate_shopping_list_pdf(shopping_list_result):
            buffer = BytesIO()  # Create a buffer to store the PDF
            pdf = canvas.Canvas(buffer, pagesize=letter)

            # Set up the PDF content
            pdf.setFont("Roboto-Black", 12)
            pdf.drawString(72, 750, "Shopping List")

            y = 730  # Starting y-position for the list
            for ingredient, amount in shopping_list_result.items():
                pdf.drawString(72, y, f"{ingredient}: {amount}")
                y -= 20  # Move down for the next item
                if y < 50:  # Add a new page if we run out of space
                    pdf.showPage()
                    y = 750

            pdf.save()
            buffer.seek(0)  # Rewind the buffer to the beginning
            return buffer

        pdfmetrics.registerFont(TTFont('Roboto-Black', 'static/Roboto-Black.ttf'))

        user = request.user

        shopping_cart = user.shopping_cart.all()
        shopping_list_result = {}

        recipes_with_ingredients = shopping_cart.prefetch_related('recipe_ingredient__ingredient')

        for recipe in recipes_with_ingredients:
            recipe_ingredients = recipe.recipe_ingredient.all()
            for recipe_ingredient_object in recipe_ingredients:
                ingredient_name = recipe_ingredient_object.ingredient.name
                if ingredient_name in shopping_list_result:
                    shopping_list_result[ingredient_name] += recipe_ingredient_object.amount
                else:
                    shopping_list_result[ingredient_name] = recipe_ingredient_object.amount

        pdf_buffer = generate_shopping_list_pdf(shopping_list_result)

        response = FileResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="shopping_cart.pdf"'
        return response


    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if user.shopping_cart.filter(pk=recipe.pk):
                return Response(
                    'Рецепт, который вы пытаетесь добавить, уже находится в списке покупок',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.shopping_cart.add(recipe)
            serializer = SimpleRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        try:
            user.shopping_cart.get(pk=recipe.pk)
        except ObjectDoesNotExist:
            return Response(
                'Рецепт, который вы пытаетесь удалить, не находится в списке покупок',
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.shopping_cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete']
    )  # Can i squish shopping_cart and favorites in one function?
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if user.favorites_list.filter(pk=recipe.pk):
                return Response(
                    'Рецепт, который вы пытаетесь добавить, уже находится в избранном',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            user.favorites_list.add(recipe)
            serializer = SimpleRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        try:
            user.favorites_list.get(pk=recipe.pk)
        except ObjectDoesNotExist:
            return Response(
                'Рецепт, который вы пытаетесь удалить, не находится в избранном',
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.favorites_list.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, url_path='get-link')
    def get_link(self, request, pk=None):
        def create_short_link(recipe):
            while True:
                short_link = ''.join(
                    random.choices(
                        string.ascii_lowercase + string.digits,
                        k=SHORT_LINK_LENGTH,
                    )
                )
                recipe.short_link = short_link
                try:
                    recipe.save()
                    return short_link
                except IntegrityError:
                    continue

        recipe = get_object_or_404(Recipe, pk=pk)
        short_link = recipe.short_link
        if not short_link:
            short_link = create_short_link(recipe)

        return Response(
            {'short-link': request.build_absolute_uri(f'/s/{short_link}')}
        )


def redirect_to_recipe(request, short_link):
    try:
        recipe = Recipe.objects.get(short_link=short_link)
        redirect_url = f'/api/recipes/{recipe.id}/'
        return redirect(redirect_url)
    except ObjectDoesNotExist:
        return Response(
            'Неправильная короткая ссылка на рецепт',
            status=status.HTTP_400_BAD_REQUEST,
        )
