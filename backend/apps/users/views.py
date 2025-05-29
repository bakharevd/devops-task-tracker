from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Position
from .permissions import IsAdminOrSelf
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    PositionSerializer
)

User = get_user_model()


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return []
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related('position').all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy', 'list']:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated(), IsAdminOrSelf()]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
