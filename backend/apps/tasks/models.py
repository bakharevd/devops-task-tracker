from django.conf import settings
from django.db import models


class Project(models.Model):
    """
    Модель проекта в системе управления задачами.

    Проект представляет собой контейнер для группировки связанных задач.
    Каждый проект имеет уникальное имя и код, а также может содержать
    множество участников (пользователей).
    """

    name = models.CharField(
        max_length=150,
        unique=True,
        help_text="Название проекта (максимум 150 символов)",
    )
    code = models.CharField(
        max_length=16,
        unique=True,
        help_text="Уникальный код проекта (максимум 16 символов)",
    )
    description = models.TextField(blank=True, help_text="Подробное описание проекта")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Дата и время создания проекта"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Дата и время последнего обновления проекта"
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="projects",
        blank=True,
        help_text="Участники проекта",
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Переопределение метода save для автоматического преобразования
        кода проекта в верхний регистр при сохранении.
        """
        if self.code:
            self.code = self.code.upper()
        super().save(*args, **kwargs)


class Status(models.Model):
    """
    Модель статуса задачи.

    Определяет возможные состояния задачи в системе (например, "Новая",
    "В работе", "Завершена" и т.д.).
    """

    name = models.CharField(
        max_length=50, unique=True, help_text="Название статуса (максимум 50 символов)"
    )

    class Meta:
        verbose_name = "Статус задачи"
        verbose_name_plural = "Статусы задач"

    def __str__(self):
        return self.name


class Priority(models.Model):
    """
    Модель приоритета задачи.

    Определяет уровни важности задачи (например, "Низкий", "Средний",
    "Высокий", "Критический").
    """

    level = models.CharField(
        max_length=50,
        unique=True,
        help_text="Уровень приоритета (максимум 50 символов)",
    )

    class Meta:
        verbose_name = "Приоритет задачи"
        verbose_name_plural = "Приоритеты задач"

    def __str__(self):
        return self.level


class Task(models.Model):
    """
    Модель задачи в системе.

    Представляет собой единицу работы, которая должна быть выполнена
    в рамках проекта. Задача имеет уникальный идентификатор, создается
    пользователем и может быть назначена другому пользователю.
    """

    issue_id = models.CharField(
        max_length=32,
        unique=True,
        editable=False,
        help_text="Уникальный идентификатор задачи в формате PROJECT-XXX",
    )
    title = models.CharField(
        max_length=200, help_text="Название задачи (максимум 200 символов)"
    )
    description = models.TextField(blank=True, help_text="Подробное описание задачи")
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Дата и время создания задачи"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Дата и время последнего обновления задачи"
    )
    due_date = models.DateTimeField(
        null=True, blank=True, help_text="Планируемая дата завершения задачи"
    )

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
        help_text="Пользователь, создавший задачу",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
        help_text="Пользователь, назначенный на задачу",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="Проект, к которому относится задача",
    )
    status = models.ForeignKey(
        Status,
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name="tasks",
        help_text="Текущий статус задачи",
    )
    priority = models.ForeignKey(
        Priority,
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name="tasks",
        help_text="Приоритет задачи",
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status.name})"

    def save(self, *args, **kwargs):
        """
        Переопределение метода save для автоматической генерации
        уникального идентификатора задачи при создании.
        """
        if not self.issue_id:
            project_code = self.project.code
            last_task = (
                Task.objects.filter(project=self.project).order_by("-id").first()
            )
            if last_task and last_task.issue_id and "-" in last_task.issue_id:
                try:
                    last_number = int(last_task.issue_id.split("-")[-1])
                except Exception:
                    last_number = Task.objects.filter(project=self.project).count()
            else:
                last_number = 0
            self.issue_id = f"{project_code}-{last_number + 1}"
        super().save(*args, **kwargs)


class Comment(models.Model):
    """
    Модель комментария к задаче.

    Позволяет пользователям оставлять комментарии к задачам и
    прикреплять файлы. Каждый комментарий связан с конкретной
    задачей и имеет автора.
    """

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Задача, к которой относится комментарий",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="Автор комментария",
    )
    text = models.TextField(help_text="Текст комментария")
    attachment = models.FileField(
        upload_to="task_attachments/",
        null=True,
        blank=True,
        help_text="Прикрепленный файл",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Дата и время создания комментария"
    )
    updated_at = models.DateTimeField(
        auto_now=True, help_text="Дата и время последнего обновления комментария"
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self):
        return f"Комментарий #{self.id} к Задаче «{self.task.title}»"
