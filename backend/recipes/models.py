from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

RECIPE_NAME_MAX_LENGTH = 30
RECIPE_TEXT_MAX_LENGTH = 50
TAG_NAME_MAX_LENGTH = 10
TAG_SLUG_MAX_LENGTH = 10
INGREDIENT_NAME_MAX_LENGTH = 50
INGREDIENT_UNITS_MAX_LENGTH = 20



class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]


class Ingredient(models.Model):
    name = models.CharField(max_length=INGREDIENT_NAME_MAX_LENGTH)
    measurement_unit = models.CharField(max_length=INGREDIENT_UNITS_MAX_LENGTH)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=TAG_NAME_MAX_LENGTH, unique=True)
    color = models.CharField(max_length=6, unique=True)
    slug = models.SlugField(max_length=TAG_SLUG_MAX_LENGTH, unique=True)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    # classsss?
    author = models.ForeignKey(
       # User, on_delete=models.CASCADE, related_name='%(class)ss'
       User, on_delete=models.CASCADE, related_name='recipes'
    )
    name = models.CharField(max_length=RECIPE_NAME_MAX_LENGTH)
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None
    )
    text = models.TextField(max_length=RECIPE_TEXT_MAX_LENGTH)
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='IngredientRecipe'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes_with_tag',
        through='TagRecipe'
    )
    # как-то указать, что в минутах
    cooking_time = models.IntegerField()
    is_favorited = models.BooleanField(default=False)
    is_in_shopping_card = models.BooleanField(default=False)

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
        null=True
    )
    recipes = models.ForeignKey(
        Recipe, on_delete=models.SET_NULL,
        null=True
    )


class ShoppingCard(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True
    )
    recipes = models.ForeignKey(
        Recipe, on_delete=models.SET_NULL,
        null=True
    )
