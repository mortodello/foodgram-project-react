from django.core.exceptions import ValidationError


def unique_ingredient(value):
    income_value = value.copy()
    for v1 in value:
        element = value.pop()
        for v2 in value:
            if element == v2:
                raise ValidationError('Такой ингредиент уже есть!')
    return income_value


def unique_tag(value):
    income_value = value.copy()
    for v1 in value:
        element = value.pop()
        for v2 in value:
            if element == v2:
                raise ValidationError('Такой тег уже есть!')
    return income_value


def tag_igredient_not_empty(value):
    print(value)
    if 'tags' not in value:
        raise ValidationError('Поле тег отсутствует!')
    if 'ingredients_used' not in value:
        raise ValidationError('Поле ингредиент отсутствует!')
    return value
