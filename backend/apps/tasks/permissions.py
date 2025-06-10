from rest_framework import permissions


class IsAuthorOrAdmin(permissions.BasePermission):
    """
    Разрешение, позволяющее редактировать объект только его автору или администратору.

    Используется для ограничения доступа к комментариям и другим объектам,
    где требуется проверка авторства.
    """

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь право на выполнение действия с объектом.

        Args:
            request: HTTP запрос
            view: ViewSet или View, обрабатывающий запрос
            obj: Объект, к которому проверяется доступ

        Returns:
            bool: True, если пользователь является автором объекта или администратором,
                 False в противном случае
        """
        if request.user.is_superuser:
            return True
        return obj.author == request.user
