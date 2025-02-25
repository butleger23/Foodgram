from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status, viewsets

from api.pagination import UserPaginationClass

from .serializers import UserSerializer, UserSubscriptionSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPaginationClass


    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        else:
            return [IsAuthenticated()]


    @action(detail=False, methods=['post'])
    def set_password(self, request):
        user = request.user
        if user.check_password(request.data.get('current_password')):
            user.set_password(request.data.get('new_password'))
            user.save()
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
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, serializer_class=UserSubscriptionSerializer)
    def subscriptions(self, request):
        subscriptions = request.user.subscriptions.prefetch_related('recipes').all()
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, pk=None):
        user = request.user
        target_user = User.objects.get(pk=pk)

        if request.method == 'POST':
            if target_user == user:
                return Response(
                    {'error': 'You cannot subscribe to yourself.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.subscriptions.add(target_user)
            serializer = UserSubscriptionSerializer(target_user, context={'request': request}) # Passing context smells
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        user.subscriptions.remove(target_user)
        return Response(status=status.HTTP_204_NO_CONTENT)
