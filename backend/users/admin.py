from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import FoodgramUser, Subscriptions


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author'
    )
    list_filter = ('author', 'name', 'tags')


class UserAdminModel(UserAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
    )
    readonly_fields = ['last_login', 'date_joined']
    list_filter = ('email', 'username')


UserAdminModel.fieldsets += (
    ('Особое', {'fields': ('role',)}),
)

admin.site.register(FoodgramUser, UserAdminModel)
admin.site.register(Subscriptions)
