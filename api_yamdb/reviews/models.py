from django.db import models


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
