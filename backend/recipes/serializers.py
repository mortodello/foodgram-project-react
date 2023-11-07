import base64
# import datetime as dt

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers
from djoser.serializers import UserSerializer

from .models import Tag, Ingredient, Recipe, IngredientRecipe, TagRecipe

from django.contrib.auth import get_user_model

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


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientRecipeSerializer(serializers.ModelSerializer):
    ingredient = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
        #source='ingredient')

    class Meta:
        model = IngredientRecipe
        fields = ('ingredient', 'amount')


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = IngredientRecipeSerializer()
    image = Base64ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'image_url','text', 'cooking_time'
        )

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class RecipePostSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(queryset=Tag.objects.all(),
                                        slug_field='id', required=True, many=True)
    ingredients = IngredientRecipeSerializer(many=True)
    image = Base64ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name', 'text', 'cooking_time', 'image', 'image_url')

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = Recipe.objects.create(**validated_data)
        for ingredient in ingredients:
            print(ingredient['ingredient'])
            IngredientRecipe.objects.create(ingredient=ingredient['ingredient'], recipe=instance, amount=ingredient['amount'])
        for tag in tags:
            TagRecipe.objects.create(tag=tag, recipe=instance)
        return instance

    #def to_representation(self, instance):
    #    representation = super(EquipmentSerializer, self).to_representation(instance)
    #    representation['assigment'] = AssignmentSerializer(instance.assigment_set.all(), many=True).data
    #    return representation

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None




