from django.utils import timezone

from django.core.validators import MaxValueValidator


def current_year():
    current_year = timezone.now().year
    return current_year


def current_year_validator(value):
    value = current_year()
    return MaxValueValidator(value)
