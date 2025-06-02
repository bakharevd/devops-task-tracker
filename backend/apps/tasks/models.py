from django.conf import settings
from django.db import models


class Project(models.Model):
    """
    Сущность Проекты
    """
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='projects',
        blank=True
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Status(models.Model):
    """
    Справочник статусов
    """
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Статус задачи'
        verbose_name_plural = 'Статусы задач'

    def __str__(self):
        return self.name


class Priority(models.Model):
    """
    Справочник приоритетов
    """
    level = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Приоритет задачи'
        verbose_name_plural = 'Приоритеты задач'

    def __str__(self):
        return self.level


class Task(models.Model):
    """
    Сущность Задачи
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_tasks'
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name='tasks'
    )
    priority = models.ForeignKey(
        Priority,
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name='tasks'
    )

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.status.name})"
