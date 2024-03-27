from django.core.exceptions import ValidationError


def unique_ingredient(value):
    if len(value) != len(set([v['ingredient'] for v in value])):
        raise ValidationError('Ингредиенты не должны дублироваться!')
    return value


def unique_tag(value):
    if len(value) != len(set(value)):
        raise ValidationError('Теги не должны дублироваться!')
    return value
