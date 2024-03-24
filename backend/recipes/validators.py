from django.core.exceptions import ValidationError


def unique_ingredient(value):
    income_value = value.copy()
    for v1 in value:
        element = value.pop()
        for v2 in value:
            if element == v2:
                raise ValidationError(f'Ингредиент {element} уже есть!')
    return income_value


def unique_tag(value):
    income_value = value.copy()
    for v1 in value:
        element = value.pop()
        for v2 in value:
            if element == v2:
                raise ValidationError(f'Тег {element} уже есть!')
    return income_value
