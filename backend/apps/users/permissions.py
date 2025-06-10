"""
Разрешения для приложения users.

Определяет классы разрешений для контроля доступа к объектам.
"""

from rest_framework import permissions


class IsAdminOrSelf(permissions.BasePermission):
    """
    Разрешение, позволяющее доступ только администраторам или владельцам объекта.

    Администраторы имеют доступ ко всем объектам.
    Обычные пользователи имеют доступ только к своим объектам.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь доступ к объекту.

        Args:
            request: HTTP запрос
            view: Представление, обрабатывающее запрос
            obj: Объект, к которому проверяется доступ

        Returns:
            bool: True если доступ разрешен, False в противном случае
        """
        if request.user.role == "admin":
            return True
        return obj == request.user
