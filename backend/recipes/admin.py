from django.contrib import admin

from .models import (Favorites, Follow, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCard, Tag, TagRecipe)


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe
    extra = 1


class TagRecipeInline(admin.TabularInline):
    model = TagRecipe
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (IngredientRecipeInline, TagRecipeInline)
    list_display = (
        'name',
        'author'
    )
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('ingredients',)


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(Favorites)
admin.site.register(Follow)
admin.site.register(ShoppingCard)
