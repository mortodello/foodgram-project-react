import base64

import webcolors
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import TokenCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import (Ingredient, IngredientRecipe, Recipe, Tag, TagRecipe,
                     Follow, Favorites)

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


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class CustomUserSerializer(UserSerializer):
    # is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')


'''
    def create(self, validated_data):
        # print(f'VALIDATED_DATA: {validated_data}')
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        instance = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            # print(ingredient['id'])
            IngredientRecipe.objects.create(
                ingredient=ingredient['ingredient'],
                recipe=instance,
                amount=ingredient['amount']
            )
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=instance)
        return instance
'''
# def to_representation(self, instance):
#    representation = super().to_representation(instance)
#    representation.pop['is_subscribed']
#    representation['password'] = serializers.CharField()
#    return representation


'''
    def get_is_subscribed(self, obj):
        print(f'OBJECT: {obj}')
        print(f'SELF: {self}')
        print(f'USER: {self.context}')
        for user in Follow.objects.all().filter(user=obj):
            print(f'FOLLOW: {user}')
        return False
'''


class GetTokenSerializer(TokenCreateSerializer):
    class Meta:
        model = User
        fields = ('password', 'email')


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

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # representation['id'] =
        # serializers.IntegerField(source='ingredient.id')
        return representation


class RecipeSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    tags = serializers.SlugRelatedField(queryset=Tag.objects.all(),
                                        slug_field='id', required=True,
                                        many=True)
    ingredients = IngredientRecipeSerializer(many=True,
                                             source='ingredients_used')
    image = Base64ImageField(required=False, allow_null=True)
    # image_url = serializers.SerializerMethodField(
    #    'get_image_url',
    #    read_only=True,
    # )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_card',
            'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('id', 'author', 'is_favorited',
                            'is_in_shopping_card')

    def create(self, validated_data):
        # print(f'VALIDATED_DATA: {validated_data}')
        ingredients = validated_data.pop('ingredients_used')
        tags = validated_data.pop('tags')
        instance = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            # print(ingredient['id'])
            IngredientRecipe.objects.create(
                ingredient=ingredient['ingredient'],
                recipe=instance,
                amount=ingredient['amount']
            )
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=instance)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tags'] = TagSerializer(instance.tags, many=True).data
        return representation
        '''
        testdata = Tag.objects.all()
        print(f'QUERYSET: {testdata}')
        print(f'QUERYSET_TYPE: {type(testdata)}')
        for test in testdata:
            print(f'OBJECT: {test}')
            print(f'OBJECT_TYPE: {type(test)}')
        testdata = Tag.objects.all().values()
        print(f'QUERYSET_VAL: {testdata}')
        print(f'QUERYSET_VAL_TYPE: {type(testdata)}')
        for test in testdata:
            print(f'VALUE: {test}')
            print(f'VALUE_TYPE: {type(test)}')
        return representation
        '''

    # def get_image_url(self, obj):
    #    if obj.image:
    #        return obj.image.url
    #    return None


class FollowSerializer(UserSerializer):
    recipes = serializers.SlugRelatedField(queryset=Recipe.objects.all(),
                                           slug_field='id', many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'recipes', 'recipes_count')
        read_only_fields = ('email', 'id', 'username', 'first_name',
                            'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['recipes'] = RecipeSerializer(instance.recipes.all(), many=True).data
        for recipe in representation['recipes']:
            recipe.pop('tags')
            recipe.pop('author')
            recipe.pop('ingredients')
            recipe.pop('is_favorited')
            recipe.pop('is_in_shopping_card')
            recipe.pop('text')
        return representation


class FavoritesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

