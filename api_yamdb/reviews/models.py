from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
from django.db import models

ROLES_CHOICES = (
    ('user', 'Аутентифицированный пользователь'),
    ('moderator', 'Модератор'),
    ('admin', 'Администратор'),
)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=30,
        choices=ROLES_CHOICES,
        default='user'
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=200,
        null=True
    )
    REQUIRED_FIELDS = ['email']


class Titles(models.Model):
    """ Определённый фильм, книга или песенка."""
    title = models.CharField(max_length=250)


class Reviews(models.Model):
    """ Отзывы на произведения."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(
        Titles, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
    rating = models.SmallIntegerField(
        validators=[MaxValueValidator(10)], default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_reviews',
                fields=['author', 'title'],
            ),
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    reviews = models.ForeignKey(
        Reviews, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
