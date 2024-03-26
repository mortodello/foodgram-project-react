from django.core.exceptions import ValidationError


def unique_ingredient(value):
    ingredient_list = []
    [ingredient_list.append(v['ingredient']) for v in value]
    if len(value) != len(set(ingredient_list)):
        raise ValidationError('Ингредиенты не должны дублироваться!')
    return value


def unique_tag(value):
    if len(value) != len(set(value)):
        raise ValidationError('Теги не должны дублироваться!')
    return value
