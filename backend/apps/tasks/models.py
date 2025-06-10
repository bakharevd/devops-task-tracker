from django.conf import settings
from django.db import models


class Project(models.Model):
    """
    Сущность Проекты
    """

    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=16, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="projects", blank=True
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.upper()
        super().save(*args, **kwargs)


class Status(models.Model):
    """
    Справочник статусов
    """

    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Статус задачи"
        verbose_name_plural = "Статусы задач"

    def __str__(self):
        return self.name


class Priority(models.Model):
    """
    Справочник приоритетов
    """

    level = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Приоритет задачи"
        verbose_name_plural = "Приоритеты задач"

    def __str__(self):
        return self.level


class Task(models.Model):
    """
    Сущность Задачи
    """

    issue_id = models.CharField(max_length=32, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)

    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_tasks"
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    status = models.ForeignKey(
        Status, on_delete=models.SET_DEFAULT, default=1, related_name="tasks"
    )
    priority = models.ForeignKey(
        Priority, on_delete=models.SET_DEFAULT, default=1, related_name="tasks"
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.status.name})"

    def save(self, *args, **kwargs):
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
    Комментарии к задаче с вложениями
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
    attachment = models.FileField(upload_to="task_attachments/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["created_at"]

    def __str__(self):
        return f"Комментарий #{self.id} к Задаче «{self.task.title}»"
