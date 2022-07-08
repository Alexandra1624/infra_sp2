from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import CharField, EmailField, TextField
from typing import Tuple, List

ADMIN: str = 'admin'
MODERATOR: str = 'moderator'
USER: str = 'user'
ME: str = 'me'

role_choices: List[Tuple[str, str]] = [
    (USER, 'user'),
    (MODERATOR, 'moderator'),
    (ADMIN, 'admin'),
]


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    username: CharField = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        help_text=(
            'Обязательное поле. До 150 символов. Буквы, цифры разрешены.'
        ),
        validators=[username_validator],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует'
        },
    )
    email: EmailField = models.EmailField(
        max_length=255, unique=True, blank=False
    )
    role: CharField = models.CharField(
        choices=role_choices, default=USER, max_length=9
    )
    bio: TextField = models.TextField(max_length=500, blank=True, null=True)
    first_name: CharField = models.CharField(max_length=50, blank=True)
    last_name: CharField = models.CharField(max_length=50, blank=True)

    confirmation_code: TextField = models.TextField(null=True, blank=True)

    exclude: Tuple[str] = ('confirmation_code',)

    class Meta:
        verbose_name: str = 'Пользователь'
        verbose_name_plural: str = 'Пользователи'

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = ADMIN
        elif self.role == ADMIN:
            self.is_staff = True
        else:
            self.is_staff = False

        super(User, self).save(*args, **kwargs)
