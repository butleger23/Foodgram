from django.contrib.auth.models import AbstractUser
from django.db import models


MAX_USERNAME_LENGTH = 150


class FoodgramUser(AbstractUser):
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )
    first_name = models.CharField('Имя', max_length=150)
    last_name = models.CharField('Фамилия', max_length=150)
    bio = models.TextField('Биография', blank=True)
    email = models.EmailField('Почта', unique=True)
    avatar = models.ImageField(
        'Аватар', upload_to='user_avatars', blank=True, null=True
    )
    subscriptions = models.ManyToManyField(
        'self', symmetrical=False, related_name='subscribers'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'Пользователь - {self.username}'
