from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    user = 'user'
    moderator = 'moderator'
    admin = 'admin'
    CHOICES = [
        (user, 'Аутентифицированный пользователь'),
        (moderator, 'Модератор'),
        (admin, 'Администратор'),
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

    def save(self, *args, **kwargs):
        if self.is_superuser is True:
            self.role = self.admin
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        return self.role == self.admin

    @property
    def is_moderator(self):
        return self.role == self.moderator

    @property
    def is_user(self):
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
