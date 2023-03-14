from django.db import models


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
