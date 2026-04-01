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
from django.contrib.auth import login
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

admin.site.site_url = "/tasks"


@csrf_exempt
def admin_auto_login(request):
    """
    Авто-логин в Django Admin через JWT-токен.

    Принимает JWT из заголовка Authorization, создаёт Django-сессию
    и перенаправляет в /admin/.
    """
    auth = JWTAuthentication()
    try:
        result = auth.authenticate(request)
        if result is None:
            return JsonResponse({"detail": "Токен не предоставлен"}, status=401)
        user, _ = result
        if not (user.is_staff or user.is_superuser):
            return JsonResponse({"detail": "Нет доступа к админ-панели"}, status=403)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("/admin/")
    except Exception:
        return JsonResponse({"detail": "Невалидный токен"}, status=401)


urlpatterns = (
    [
        # Авто-логин в админку через JWT
        path("api/admin-login/", admin_auto_login, name="admin_auto_login"),
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
