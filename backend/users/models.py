from django.contrib.auth.models import AbstractUser
from django.db import models


USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLES = (
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор'),
)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=max([len(x) for (x, _) in ROLES]),
        choices=ROLES,
        default=USER
    )
    is_subscribed = models.BooleanField(null=True)

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
