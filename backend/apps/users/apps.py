"""
Конфигурация приложения users.

Определяет основные настройки приложения пользователей.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "apps.users"
    verbose_name = "Пользователи"
