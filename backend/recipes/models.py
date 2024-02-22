from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()

RECIPE_NAME_MAX_LENGTH = 30
RECIPE_TEXT_MAX_LENGTH = 50
TAG_NAME_MAX_LENGTH = 10
TAG_SLUG_MAX_LENGTH = 10
INGREDIENT_NAME_MAX_LENGTH = 50
INGREDIENT_UNITS_MAX_LENGTH = 20


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers',
        verbose_name='Пользователь')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='Подписан на')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]
        verbose_name = 'Подписки'
        verbose_name_plural = 'подписки'

    def __str__(self):
        return self.user.username


class Ingredient(models.Model):
    name = models.CharField(max_length=INGREDIENT_NAME_MAX_LENGTH,
                            verbose_name='Название')
    measurement_unit = models.CharField(max_length=INGREDIENT_UNITS_MAX_LENGTH,
                                        verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=TAG_NAME_MAX_LENGTH, unique=True,
                            verbose_name='Название')
    color = models.CharField(max_length=6, unique=True, verbose_name='Цвет')
    slug = models.SlugField(max_length=TAG_SLUG_MAX_LENGTH, unique=True,
                            verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    # classsss?
    author = models.ForeignKey(
        # User, on_delete=models.CASCADE, related_name='%(class)ss'
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=RECIPE_NAME_MAX_LENGTH,
                            verbose_name='Название')
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None, verbose_name='Изображение'
    )
    text = models.TextField(max_length=RECIPE_TEXT_MAX_LENGTH,
                            verbose_name='Текст')
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientRecipe', verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes_with_tag',
        through='TagRecipe', verbose_name='Теги'
    )
    # как-то указать, что в минутах
    cooking_time = models.IntegerField(verbose_name='Время приготовления')
    is_favorited = models.BooleanField(default=False,
                                       verbose_name='В избранном')
    is_in_shopping_card = models.BooleanField(default=False,
                                              verbose_name='В списке покупок')

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        Tag, on_delete=models.SET_NULL,
        null=True, blank=True
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.SET_NULL,
        null=True, blank=True
    )


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='ingredients_used'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name='recipes_used'
    )
    amount = models.FloatField()


class Favorites(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, verbose_name='Пользователь'
    )
    recipes = models.ForeignKey(
        Recipe, on_delete=models.SET_NULL,
        related_name='favorite_recipe',
        null=True, verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return self.user.username


class ShoppingCard(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, verbose_name='Пользователь'
    )
    recipes = models.ForeignKey(
        Recipe, on_delete=models.SET_NULL,
        null=True, verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return self.user.username
