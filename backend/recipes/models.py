from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (AMOUNT_MAX_MESSAGE, AMOUNT_MAX_VALUE,
                        AMOUNT_MIN_MESSAGE, AMOUNT_MIN_VALUE,
                        COOKING_MAX_MESSAGE, COOKING_MAX_VALUE,
                        COOKING_MIN_MESSAGE, COOKING_MIN_VALUE,
                        INGREDIENT_NAME_MAX_LENGTH,
                        INGREDIENT_UNITS_MAX_LENGTH, RECIPE_NAME_MAX_LENGTH,
                        TAG_COLOR_MAX_LENGTH, TAG_NAME_MAX_LENGTH,
                        TAG_SLUG_MAX_LENGTH)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=INGREDIENT_NAME_MAX_LENGTH,
                            verbose_name='Название')
    measurement_unit = models.CharField(max_length=INGREDIENT_UNITS_MAX_LENGTH,
                                        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    constraints = [
        models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_name_measurement_unit'
        )
    ]

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=TAG_NAME_MAX_LENGTH, unique=True,
                            verbose_name='Название')
    color = models.CharField(max_length=TAG_COLOR_MAX_LENGTH,
                             unique=True, verbose_name='Цвет')
    slug = models.SlugField(max_length=TAG_SLUG_MAX_LENGTH, unique=True,
                            verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=RECIPE_NAME_MAX_LENGTH,
                            verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Текст')
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientRecipe', verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes_with_tag',
        verbose_name='Теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(COOKING_MIN_VALUE, COOKING_MIN_MESSAGE),
            MaxValueValidator(COOKING_MAX_VALUE, COOKING_MAX_MESSAGE)
        ])
    is_favorited = models.BooleanField(default=False,
                                       verbose_name='В избранном')
    is_in_shopping_cart = models.BooleanField(default=False,
                                              verbose_name='В списке покупок')

    class Meta:
        ordering = ['-id']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredients_used'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipes_used'
    )
    amount = models.PositiveSmallIntegerField('Количество', validators=[
        MinValueValidator(AMOUNT_MIN_VALUE, AMOUNT_MIN_MESSAGE),
        MaxValueValidator(AMOUNT_MAX_VALUE, AMOUNT_MAX_MESSAGE)
    ])


class BaseFavoriteShopping(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_favorite'
            )
        ]


class Favorite(BaseFavoriteShopping):

    class Meta:
        default_related_name = 'favorite_recipe'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return (f'{self.user.username} добавил'
                f'{self.recipe.name} в избранное')


class ShoppingCart(BaseFavoriteShopping):

    class Meta:
        default_related_name = 'carts'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return (f'{self.user.username} добавил'
                f'{self.recipe.name} в список покупок')
