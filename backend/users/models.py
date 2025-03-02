from django.contrib.auth.models import AbstractUser
from django.db import models


MAX_USERNAME_LENGTH = MAX_FIRST_NAME_LENGTH = MAX_LAST_NAME_LENGTH = 150


class FoodgramUser(AbstractUser):
    first_name = models.CharField('Имя', max_length=MAX_FIRST_NAME_LENGTH)
    last_name = models.CharField('Фамилия', max_length=MAX_LAST_NAME_LENGTH)
    bio = models.TextField('Биография', blank=True)
    email = models.EmailField('Почта', unique=True)
    avatar = models.ImageField(
        'Аватар', upload_to='user_avatars', blank=True, null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['last_name', 'first_name', 'username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'Пользователь - {self.username}'


class Subscriptions(models.Model):
    subscriber = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, related_name='subscriptions'
    )
    subscribed_to = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, related_name='subscribers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('subscriber', 'subscribed_to'),
                name='unique_subscriber_subscribed_to',
            )
        ]

    def __str__(self):
        return f'{self.subscriber} subscribed to {self.subscribed_to}'
