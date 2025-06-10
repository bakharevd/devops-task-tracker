"""
Корневые URL-маршруты проекта.

Определяет основные маршруты для:
- Административного интерфейса
- JWT аутентификации
- API эндпоинтов пользователей и задач
- Статических и медиа файлов
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

admin.site.site_url = "/tasks"

urlpatterns = (
    [
        # Административный интерфейс
        path("admin/", admin.site.urls),
        # JWT аутентификация
        path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
        path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
        # API эндпоинты
        path("api/users/", include("apps.users.urls")),
        path("api/tasks/", include("apps.tasks.urls")),
    ]
    # Статические и медиа файлы
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
