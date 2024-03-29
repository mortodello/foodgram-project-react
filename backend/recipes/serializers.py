import base64

import webcolors
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import TokenCreateSerializer, UserSerializer
from rest_framework import serializers

from users.models import Subscriptions

from .constants import (AMOUNT_MIN_VALUE,
                        AMOUNT_MIN_MESSAGE,
                        AMOUNT_MAX_VALUE,
                        AMOUNT_MAX_MESSAGE,
                        COOKING_MIN_VALUE,
                        COOKING_MIN_MESSAGE,
                        COOKING_MAX_VALUE,
                        COOKING_MAX_MESSAGE)
from .models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                     ShoppingCart, Tag)
from .validators import unique_ingredient, unique_tag

User = get_user_model()


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class FoodgramUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password', 'is_subscribed')

    def get_fields(self):
        fields = super().get_fields()
        if self.context['request'].method == 'POST':
            fields.pop('is_subscribed')
        return fields

    def get_is_subscribed(self, obj):
        return (self.context['request'].user.is_authenticated
                and Subscriptions.objects.filter(
                    following=self.context['request'].user,
                    follower=obj).exists())

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password')
        return representation

    def create(self, validated_data):
        password = make_password(validated_data.pop('password'))
        validated_data['password'] = password
        return super().create(validated_data)


class GetTokenSerializer(TokenCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.SlugRelatedField(queryset=Ingredient.objects.all(),
                                      slug_field='id', required=True,
                                      source='ingredient')
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('name', 'measurement_unit')

    def validate_amount(self, value):
        if value < AMOUNT_MIN_VALUE:
            raise serializers.ValidationError(AMOUNT_MIN_MESSAGE)
        if value > AMOUNT_MAX_VALUE:
            raise serializers.ValidationError(AMOUNT_MAX_MESSAGE)
        return value


class RecipeSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientRecipeSerializer(many=True,
                                             source='ingredients_used')
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )
        read_only_fields = ('id', 'author', 'is_favorited',
                            'is_in_shopping_cart')

    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user__id=self.context['request'].user.id,
            recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        return ShoppingCart.objects.filter(
            user__id=self.context['request'].user.id,
            recipe=obj).exists()

    def validate(self, data):
        if 'tags' not in data:
            raise serializers.ValidationError('Поле тег отсутствует!')
        if 'ingredients_used' not in data:
            raise serializers.ValidationError('Поле ингредиент отсутствует!')
        return data

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError('Поле не должно быть пустым!')
        return unique_tag(value)

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError('Поле не должно быть пустым!')
        return unique_ingredient(value)

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError('Поле не должно быть пустым!')
        return value

    def validate_cooking_time(self, value):
        if value < COOKING_MIN_VALUE:
            raise serializers.ValidationError(COOKING_MIN_MESSAGE)
        if value > COOKING_MAX_VALUE:
            raise serializers.ValidationError(COOKING_MAX_MESSAGE)
        return value

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        instance = Recipe.objects.create(**validated_data)
        IngredientRecipe.objects.bulk_create([
            IngredientRecipe(
                ingredient=ingredient.get('ingredient'),
                recipe=instance,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ])
        instance.tags.set(tags)
        return instance

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.ingredients.clear()
        instance.tags.set(tags)
        super().update(instance, validated_data)
        ingredient_list = []
        for ingredient in ingredients:
            current_ingredient = get_object_or_404(
                Ingredient,
                name=ingredient.get('ingredient')
            )
            amount = ingredient.get('amount')
            ingredient_list.append(IngredientRecipe(
                recipe=instance,
                ingredient=current_ingredient,
                amount=amount
            ))
        IngredientRecipe.objects.bulk_create(ingredient_list)
        instance.save()
        return instance

    def to_representation(self, instance):
        path = self.context['request'].path
        parts_of_path = ['/favorite/', '/subscr', '/shop']
        if any(parts in path for parts in parts_of_path):
            short_representation = super().to_representation(instance)
            short_representation.pop('tags')
            short_representation.pop('author')
            short_representation.pop('ingredients')
            short_representation.pop('is_favorited')
            short_representation.pop('is_in_shopping_cart')
            short_representation.pop('text')
            return short_representation
        full_representation = super().to_representation(instance)
        full_representation['tags'] = TagSerializer(
            instance.tags, many=True).data
        return full_representation


class SubscriptionsSerializer(UserSerializer):
    recipes = RecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class SubscriptionsPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscriptions
        fields = ('follower', 'following')

    def validate(self, data):
        if data['follower'] == data['following']:
            raise serializers.ValidationError('Нельзя подписаться на себя!')
        if Subscriptions.objects.filter(
            follower=data['follower'].id,
            following=data['following'].id
        ).exists():
            raise serializers.ValidationError('Вы уже подписаны!')
        return data


class ShoppigCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        if not Recipe.objects.filter(id=data['recipe'].id).exists():
            raise serializers.ValidationError('Такой рецепт не существует!')
        if ShoppingCart.objects.filter(
            user=data['user'].id, recipe=data['recipe'].id
        ).exists():
            raise serializers.ValidationError('Этот рецепт уже в покупках!')
        return data


class FavoriteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        if not Recipe.objects.filter(id=data['recipe'].id).exists():
            raise serializers.ValidationError('Такой рецепт не существует!')
        if Favorite.objects.filter(user=data['user'].id,
                                   recipe=data['recipe'].id).exists():
            raise serializers.ValidationError('Этот рецепт уже в избранном!')
        return data
