# Generated by Django 3.2.16 on 2024-03-29 13:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import users.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodgramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=150, unique=True, validators=[users.validators.validate_username], verbose_name='Имя пользователя')),
                ('first_name', models.CharField(max_length=150, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=150, verbose_name='Фамилия')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Почта')),
                ('password', models.CharField(max_length=150, unique=True, verbose_name='Пароль')),
                ('last_login', models.DateTimeField(auto_now_add=True, verbose_name='Последнее посещение')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('role', models.CharField(choices=[('user', 'Пользователь'), ('moderator', 'Модератор'), ('admin', 'Администратор')], default='user', max_length=100, verbose_name='Роль')),
                ('is_subscribed', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
                'ordering': ('date_joined',),
            },
        ),
        migrations.CreateModel(
            name='Subscriptions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL, verbose_name='Подписан на')),
            ],
            options={
                'verbose_name': 'Подписки',
                'verbose_name_plural': 'подписки',
            },
        ),
        migrations.AddConstraint(
            model_name='subscriptions',
            constraint=models.UniqueConstraint(fields=('follower', 'following'), name='unique_follower_following'),
        ),
    ]
