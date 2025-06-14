"""
Административный интерфейс для приложения users.

Определяет настройки отображения моделей пользователей и должностей
в административном интерфейсе Django.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.html import format_html

from .models import Position, User


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """
    Административный интерфейс для модели Position.

    Настраивает отображение списка должностей с возможностью
    поиска и сортировки.
    """

    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Административный интерфейс для модели User.

    Расширяет стандартный UserAdmin дополнительными полями и
    настройками отображения пользователей.
    """

    model = User
    list_display = (
        "id",
        "avatar_preview",
        "email",
        "username",
        "first_name",
        "last_name",
        "position",
        "role",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("role", "position", "is_staff", "is_active")
    search_fields = ("email", "username")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (
            "Персональные данные",
            {"fields": ("first_name", "last_name", "position", "avatar")},
        ),
        (
            "Права доступа",
            {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups")},
        ),
        ("Дополнительно", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "first_name",
                    "last_name",
                    "position",
                    "role",
                    "avatar",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    def avatar_preview(self, obj):
        """
        Возвращает HTML-представление аватара пользователя.

        Args:
            obj: Объект пользователя

        Returns:
            str: HTML-код для отображения аватара
        """
        return format_html(
            '<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 50%;" />',
            obj.avatar_url,
        )

    avatar_preview.short_description = "Аватар"
