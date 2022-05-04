from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
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
    password = models.CharField(
        'Пароль',
        max_length=200,
        null=True
    )


class Category(models.Model):
    """Категории, разделы"""
    name = models.CharField(
        verbose_name='Категория',
        unique=True,
        max_length=200
    )
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Genre(models.Model):
    """Жанр произведения.

    Добавить новые жанры может только
    администратор.
    """
    name = models.CharField(
        verbose_name='Жанр',
        unique=True,
        max_length=200
    )
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug


class Title(models.Model):
    """ Определённый фильм, книга или песенка."""
    name = models.CharField(
        verbose_name='Название',
        max_length=250
    )
    year = models.IntegerField(
        verbose_name='Дата выпуска'
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=250,
    )
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        db_index=True,
        related_name='titles',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Категория'
    )

    def __str__(self):
        return self.name


class Review(models.Model):
    """ Отзывы на произведения."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.SmallIntegerField(
        'Оценка',
        validators=[MaxValueValidator(10), MinValueValidator(1)],
        default=1)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                name='unique_reviews',
                fields=['author', 'title'],
            ),
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата комментария',
        auto_now_add=True,
        db_index=True
    )

    def __str__(self):
        return self.author
