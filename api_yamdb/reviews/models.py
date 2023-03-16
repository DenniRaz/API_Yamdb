from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = [
        (ADMIN, 'Administrator'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    ]

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        unique=True,
    )
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        null=True,
        unique=True
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=50,
        choices=ROLES,
        default=USER
    )
    bio = models.TextField(
        verbose_name='О себе',
        null=True,
        blank=True
    )


class Category(models.Model):
    """Модель для категорий"""

    name = models.CharField(
        verbose_name='Название Категории',
        max_length=120
    )
    slug = models.SlugField(
        verbose_name='ID',
        max_length=99,
        unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель для жанров"""

    name = models.CharField(
        verbose_name='Название',
        max_length=120
    )
    slug = models.SlugField(
        verbose_name='ID',
        max_length=99,
        unique=True
    )

    class Meta:
        verbose_name = 'Жанр'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для произведений"""

    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    year = models.IntegerField(
        verbose_name='Дата выхода',
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True
    )

    class Meta:
        verbose_name = 'Произведение'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    SCORE_CHOICES = [
        (ONE, '1 - отвратительное произведение.'),
        (TWO, '2 - ужасное произведение.'),
        (THREE, '3 - плохое произведение.'),
        (FOUR, '4 - посредственное произведение'),
        (FIVE, '5 - среднее произведение.'),
        (SIX, '6 - неплохое произведение.'),
        (SEVEN, '7 - хорошое произведение.'),
        (EIGHT, '8 - очень хорошое произведение.'),
        (NINE, '9 - великолепное произведение.'),
        (TEN, '10 - потрясающее произведение.'),
    ]
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    text = models.TextField(
        max_length=1000,
        verbose_name='Текст отзыва',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )
    score = models.IntegerField(
        choices=SCORE_CHOICES,
        verbose_name='Рейтинг произведения',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания отзыва',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title, author'],
                name='unique_review'
            ),
        ]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )
    text = models.TextField(
        max_length=1000,
        verbose_name='Текст комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания комментария',
    )
