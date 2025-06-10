"""
Конфигурация приложения tasks.

Определяет основные настройки и метаданные приложения tasks,
которое отвечает за управление задачами, проектами и связанными сущностями.
"""

from django.apps import AppConfig


class TasksConfig(AppConfig):
    name = "apps.tasks"
