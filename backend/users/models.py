from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import CustomUserManager
from .validators import validate_username

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)
USERNAME_MAX_LENGTH = 150
FIRST_NAME_MAX_LENGTH = 150
LAST_NAME_MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254
PASSWORD_MAX_LENGTH = 150


class CustomUser(AbstractBaseUser, PermissionsMixin):
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
        max_length=max([len(x) for (x, _) in ROLES]),
        choices=ROLES,
        default=USER,
        verbose_name='Роль'
    )
    is_subscribed = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username',]

    objects = CustomUserManager()

    class Meta:
        ordering = ('date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username
