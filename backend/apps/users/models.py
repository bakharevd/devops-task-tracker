from django.contrib.auth.models import AbstractUser
from django.db import models


class Position(models.Model):
    """
    Должности сотрудников
    """
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Расширенная модель AbstractUser
    """
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('admin', 'Администратор'),
    )
    first_name = models.CharField(max_length=25)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user',
        verbose_name='Роль'
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
    
    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        import hashlib
        hash_email = hashlib.sha256(self.email.lower().strip().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{hash_email}?s=256&d=identicon&r=PG'
        
