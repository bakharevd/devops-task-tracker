from django.contrib.auth.models import AbstractUser
from django.db import models


class Position(models.Model):
    """
    Модель должности сотрудника.

    Используется для хранения списка должностей, которые могут быть
    назначены пользователям системы.
    """

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Название должности (максимум 100 символов)",
    )

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"

    def __str__(self):
        """
        Возвращает строковое представление должности.

        Returns:
            str: Название должности
        """
        return self.name


class User(AbstractUser):
    """
    Расширенная модель пользователя системы.

    Наследуется от AbstractUser и добавляет дополнительные поля:
    - Должность (связь с моделью Position)
    - Роль пользователя (user/admin)
    - Аватар пользователя
    - Обязательные поля: email, first_name, last_name
    """

    ROLE_CHOICES = (
        ("user", "Пользователь"),
        ("admin", "Администратор"),
    )
    first_name = models.CharField(
        max_length=25, help_text="Имя пользователя (максимум 25 символов)"
    )
    last_name = models.CharField(
        max_length=50, help_text="Фамилия пользователя (максимум 50 символов)"
    )
    email = models.EmailField(
        unique=True, help_text="Email пользователя (используется для входа)"
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        help_text="Должность пользователя",
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="user",
        verbose_name="Роль",
        help_text="Роль пользователя в системе",
    )
    avatar = models.ImageField(
        upload_to="avatars/", null=True, blank=True, help_text="Аватар пользователя"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        """
        Возвращает строковое представление пользователя.

        Returns:
            str: Email пользователя
        """
        return self.email

    @property
    def avatar_url(self):
        """
        Возвращает URL аватара пользователя.

        Если у пользователя есть загруженный аватар, возвращает его URL.
        В противном случае генерирует URL для Gravatar на основе email.

        Returns:
            str: URL аватара пользователя
        """
        if self.avatar:
            return self.avatar.url
        import hashlib

        hash_email = hashlib.sha256(
            self.email.lower().strip().encode("utf-8")
        ).hexdigest()
        return f"https://www.gravatar.com/avatar/{hash_email}?s=256&d=identicon&r=PG"
