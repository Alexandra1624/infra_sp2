from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Genre, Title, Comment, Review
from users.models import ADMIN, ME
from users.models import User


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')
        extra_kwargs = {'email': {'required': True}}
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=('email', 'username')
            )
        ]

    def validate(self, data):
        if data['username'] == ME:
            raise serializers.ValidationError("Имя me недопустимо!")
        return data


class VerificationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code', 'token')

    def validate(self, data):
        confirmation_code = data.get('confirmation_code')
        conf_code = get_object_or_404(
            User,
            username=data['username']
        ).confirmation_code
        if confirmation_code is None:
            raise serializers.ValidationError(
                'A confirmation_code is required to log in.'
            )
        elif confirmation_code != conf_code:
            raise serializers.ValidationError(
                'Confirmation code is invalid'
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = ('username', 'email', 'username', 'first_name', 'last_name',
                  'bio', 'role')


class CheckMeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(read_only=True)

    class Meta(object):
        model = User
        fields = ('username', 'email', 'username', 'first_name', 'last_name',
                  'bio', 'role')

    def validate(self, data):
        instance = getattr(self, 'instance')
        if instance.role != ADMIN:
            data['role'] = instance.role
        return data


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.CharField(
        allow_blank=False,
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )

    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(
        allow_blank=False,
        validators=[UniqueValidator(queryset=Genre.objects.all())]
    )

    class Meta:
        exclude = ('id',)
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(many=False, read_only=True)
    rating = serializers.FloatField(
        source='reviews__score__avg',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title

    def validate_year(self, value):
        current_year = timezone.now().year
        if not 0 <= value <= current_year:
            raise serializers.ValidationError(
                'Неверный год создания.'
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)
    title = serializers.SlugRelatedField(slug_field='id', read_only=True)

    def validate(self, data):
        if self.context['request'].method == 'POST':
            user = self.context['request'].user
            title_id = self.context['view'].kwargs.get('title_id')
            if Review.objects.filter(
                    author_id=user.id, title_id=title_id
            ).exists():
                raise serializers.ValidationError('У вас уже есть отзыв!')
        return data

    def validate_rating(value):
        if 1 > value > 10:
            raise serializers.ValidationError(
                'Оценка должна быть от 1 до 10'
            )
        return value

    class Meta:
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
