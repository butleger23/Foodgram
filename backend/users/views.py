from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.pagination import CustomPaginationClass
from users.models import Subscriptions
from .serializers import (
    UserAvatarSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserSubscriptionSerializer,
)


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPaginationClass

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'avatar' and self.request.method == 'PUT':
            return UserAvatarSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ('list', 'create', 'retrieve', 'get_token'):
            return [AllowAny()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def set_password(self, request):
        user = request.user
        if user.check_password(request.data.get('current_password')):
            user.set_password(request.data.get('new_password'))
            user.save()
        else:
            return Response(
                {'error': 'Неправильный пароль.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['put', 'delete'], url_path='me/avatar')
    def avatar(self, request):
        user = request.user
        if request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.fields['avatar'].required = True
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, serializer_class=UserSubscriptionSerializer)
    def subscriptions(self, request):
        recipes_limit = request.query_params.get('recipes_limit', None)
        subscriptions = Subscriptions.objects.filter(
            subscriber=request.user
        ).select_related('subscribed_to')
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = UserSubscriptionSerializer(
                [sub.subscribed_to for sub in page],
                many=True,
                context={'request': request, 'recipes_limit': recipes_limit},
            )
            return self.get_paginated_response(serializer.data)
        serializer = UserSubscriptionSerializer(
            [sub.subscribed_to for sub in subscriptions],
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        recipes_limit = request.query_params.get('recipes_limit', None)
        user = request.user
        try:
            target_user = User.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(
                {'error': 'Target user does not exist.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        if request.method == 'POST':
            if target_user == user:
                return Response(
                    {'error': 'You cannot subscribe to yourself.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if Subscriptions.objects.filter(
                subscriber=user, subscribed_to=target_user
            ).exists():
                return Response(
                    {'error': 'You are already subscribed to this user.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            Subscriptions.objects.create(
                subscriber=user, subscribed_to=target_user
            )
            serializer = UserSubscriptionSerializer(
                target_user,
                context={'request': request, 'recipes_limit': recipes_limit},
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            subscription = Subscriptions.objects.filter(
                subscriber=user, subscribed_to=target_user
            ).first()
            if not subscription:
                return Response(
                    {'error': 'You are not subscribed to this user.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
