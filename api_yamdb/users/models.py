from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель создания пользователя."""

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    USER_ROLES = [
        (USER, 'Аутентифицированный пользователь'),
        (MODERATOR, 'Модератор'),
        (ADMIN, 'Администратор'),
    ]
    bio = models.TextField(
        blank=True,
        verbose_name='Биография пользователя',
    )
    role = models.CharField(
        max_length=16,
        default='user',
        choices=USER_ROLES,
        verbose_name='Роль пользователя',
    )
    confirmation_code = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name='Токен пользователя',
    )

    def save(self, *args, **kwargs):
        """Создание суперпользователя с правами администратора."""
        if self.is_superuser is True:
            self.role = self.ADMIN
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        """Проверка пользователя на наличие прав администратора."""
        return self.role == self.ADMIN

    @property
    def is_moderator(self):
        """Проверка пользователя на наличие прав модератора."""
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        """Проверка пользователя на наличие стандартных прав."""
        return self.role == self.USER

    class Meta:
        ordering = ('username',)

    def __str__(self):
        return self.username
