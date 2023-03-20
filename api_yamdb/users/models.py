from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_user = 'user'
    is_moderator = 'moderator'
    is_admin = 'admin'
    CHOICES = [
        (is_user, 'Аутентифицированный пользователь'),
        (is_moderator, 'Модератор'),
        (is_admin, 'Администратор'),
    ]

    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        choices=CHOICES,
        default='user',
        max_length=16,
    )


@property
def is_admin(self):
    return self.role == self.admin


@property
def is_moderator(self):
    return self.role == self.moderator


@property
def is_authenticated(self):
    return self.role == self.user


class EmailVerification(models.Model):
    username = models.CharField(
        max_length=150,
        null=True,
    )
    confirmation_code = models.CharField(
        max_length=6,
        null=True,
    )
