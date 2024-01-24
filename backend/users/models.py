from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import CustomUserManager

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=40, unique=True, verbose_name='Имя пользователя')
    first_name = models.CharField(max_length=40, verbose_name='Имя')
    last_name = models.CharField(max_length=40, verbose_name='Фамилия')
    email = models.EmailField(max_length=40, unique=True, verbose_name='Почта')
    password = models.CharField(max_length=150, unique=True, verbose_name='Пароль')
    last_login = models.DateTimeField(auto_now_add=True, verbose_name='Последнее посещение')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    role = models.CharField(
        max_length=max([len(x) for (x, _) in ROLES]),
        choices=ROLES,
        default=USER,
        verbose_name='Роль'
    )
    is_subscribed = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        ordering = ('date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

# property вернули )) как я понял по пермишенам,
# is_superuser существует по умолчанию, а is_stuff валит тесты
# с ошибкой: TypeError:
# CustomUser() got an unexpected keyword argument 'is_staff'
    @property
    def is_admin(self):
        if self.role == ADMIN:
            return True
        return False

    @property
    def is_moderator(self):
        if self.role == MODERATOR:
            return True
        return False
