from rest_framework import serializers

from users.models import User


def check_username(username):
    if not User.objects.filter(username=username).exists():
        raise serializers.ValidationError(
            'Пользователя с таким именем не существует'
        )
