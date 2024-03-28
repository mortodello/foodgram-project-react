from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .constants import (EMAIL_MAX_LENGTH, FIRST_NAME_MAX_LENGTH,
                        LAST_NAME_MAX_LENGTH, PASSWORD_MAX_LENGTH,
                        ROLE_MAX_LEN, ROLES, USER, ADMIN, MODERATOR,
                        USERNAME_MAX_LENGTH)
from .managers import FoodgramManager
from .validators import validate_username


class FoodgramUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=USERNAME_MAX_LENGTH, unique=True,
                                validators=[validate_username, ],
                                verbose_name='Имя пользователя')
    first_name = models.CharField(max_length=FIRST_NAME_MAX_LENGTH,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=LAST_NAME_MAX_LENGTH,
                                 verbose_name='Фамилия')
    email = models.EmailField(max_length=EMAIL_MAX_LENGTH, unique=True,
                              verbose_name='Почта')
    password = models.CharField(max_length=PASSWORD_MAX_LENGTH, unique=True,
                                verbose_name='Пароль')
    last_login = models.DateTimeField(auto_now_add=True,
                                      verbose_name='Последнее посещение')
    date_joined = models.DateTimeField(auto_now_add=True,
                                       verbose_name='Дата регистрации')
    role = models.CharField(
        max_length=ROLE_MAX_LEN,
        choices=ROLES,
        default=USER,
        verbose_name='Роль'
    )
    is_subscribed = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = FoodgramManager()

    class Meta:
        ordering = ('date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR


class Subscriptions(models.Model):
    follower = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE,
        verbose_name='Пользователь')
    following = models.ForeignKey(
        FoodgramUser, on_delete=models.CASCADE, related_name='following',
        verbose_name='Подписан на')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique_follower_following'
            )
        ]
        verbose_name = 'Подписки'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return (f'{self.follower.username}'
                f'подписан на {self.following.username}')
