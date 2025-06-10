"""
Сериализаторы для приложения users.

Определяет сериализаторы для преобразования моделей пользователей
и должностей в JSON и обратно.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Position

User = get_user_model()


class PositionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Position.

    Сериализует только id и название должности.
    """

    class Meta:
        model = Position
        fields = ["id", "name"]


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели User.

    Предоставляет полную сериализацию данных пользователя, включая
    связанную должность и аватар. Поддерживает создание и обновление
    пользователей с хешированием пароля.
    """

    position = PositionSerializer(read_only=True)
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        write_only=True,
        source="position",
        help_text="ID должности пользователя",
    )
    avatar = serializers.ImageField(
        required=False, allow_null=True, help_text="Аватар пользователя"
    )
    avatar_url = serializers.SerializerMethodField()
    password = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Пароль пользователя (только для записи)",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "position",
            "position_id",
            "avatar",
            "avatar_url",
            "is_superuser",
            "password",
        ]
        read_only_fields = ["id", "is_superuser", "avatar_url"]

    def get_avatar_url(self, obj):
        """
        Возвращает URL аватара пользователя.

        Args:
            obj: Объект пользователя

        Returns:
            str: URL аватара
        """
        return obj.avatar_url

    def create(self, validated_data):
        """
        Создает нового пользователя с хешированным паролем.

        Args:
            validated_data: Валидированные данные пользователя

        Returns:
            User: Созданный пользователь
        """
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания нового пользователя.

    Используется при регистрации новых пользователей.
    Включает только необходимые поля для создания.
    """

    position_id = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        write_only=True,
        source="position",
        help_text="ID должности пользователя",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "position_id",
            "is_superuser",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        """
        Создает нового пользователя с хешированным паролем.

        Args:
            validated_data: Валидированные данные пользователя

        Returns:
            User: Созданный пользователь
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
