from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (
    ('user', 'Аутентифицированный пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
)


class User(AbstractUser):
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        choices=CHOICES,
        default='user',
        max_length=16,
    )


class EmailVerification(models.Model):
    username = models.CharField(
        max_length=150,
        null=True,
    )
    confirmation_code = models.CharField(
        max_length=6,
        null=True,
    )
