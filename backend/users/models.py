from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models



# from users.constants import MAX_USERNAME_LENGTH, MAX_USER_ROLE_LENGTH
# from users.validators import validate_forbidden_username

MAX_USERNAME_LENGTH = 20

class FoodgramUser(AbstractUser):
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        # validators=[UnicodeUsernameValidator(), validate_forbidden_username],
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )
    bio = models.TextField('Биография', blank=True)
    email = models.EmailField('Почта', unique=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'Пользователь - {self.username}'
