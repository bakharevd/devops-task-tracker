"""
Представления для приложения users.

Определяет ViewSet'ы для работы с пользователями и их должностями.
"""

from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Position
from .permissions import IsAdminOrSelf
from .serializers import UserSerializer, UserCreateSerializer, PositionSerializer

User = get_user_model()


class PositionViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления должностями пользователей.

    Предоставляет CRUD операции для должностей. Просмотр списка и деталей
    доступен всем, остальные операции только администраторам.
    """

    queryset = Position.objects.all()
    serializer_class = PositionSerializer

    def get_permissions(self):
        """
        Определяет права доступа для различных действий.

        Returns:
            list: Список классов разрешений
        """
        if self.action in ["list", "retrieve"]:
            return []
        return [permissions.IsAuthenticated(), permissions.IsAdminUser()]


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления пользователями системы.

    Предоставляет CRUD операции для пользователей с различными
    уровнями доступа в зависимости от роли пользователя.
    """

    queryset = User.objects.select_related("position").all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Определяет права доступа для различных действий.

        - Создание, удаление и просмотр списка доступны только администраторам
        - Остальные операции доступны администраторам и владельцам записей

        Returns:
            list: Список классов разрешений
        """
        if self.action in ["create", "destroy", "list"]:
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return [permissions.IsAuthenticated(), IsAdminOrSelf()]

    def get_serializer_class(self):
        """
        Определяет класс сериализатора в зависимости от действия.

        Returns:
            class: Класс сериализатора
        """
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Возвращает информацию о текущем пользователе.

        Args:
            request: HTTP запрос

        Returns:
            Response: Данные текущего пользователя
        """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
