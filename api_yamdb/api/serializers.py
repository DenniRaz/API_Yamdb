import re

from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from reviews.models import Category, Comment, Genre, Review, Title

from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    """Serializer для категории."""

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Serializer для жанра."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    """Serializer для произведения."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        required=True,
        many=True,
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all(),
        required=True,
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        if value > timezone.now().year:
            raise ValidationError(
                'Год не может быть больше текущего'
            )
        return value


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        required=False
    )
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'description',
            'genre',
            'category',
            'rating',
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer для отзыва."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('id', 'pub_date',)

    def validate(self, attrs):
        if self.context['request'].method != 'POST':
            return attrs
        user = self.context['request'].user
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        title = get_object_or_404(Title, pk=title_id)
        if Review.objects.filter(author=user, title=title).exists():
            raise serializers.ValidationError(
                'На одно произведение можно написать один отзыв!'
            )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Serializer для комментария."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('id', 'pub_date',)


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    email = serializers.EmailField(
        max_length=254,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        lookup_field = 'username'

    def validate_email(self, value):
        if value in User.objects.values_list('email', flat=True):
            raise serializers.ValidationError('Указанный email используется')
        return value


class SignUpSerializer(serializers.ModelSerializer):
    """Serializer для создания нового пользователя."""

    email = serializers.EmailField(
        max_length=254,
        required=True,
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError('Имя me недоступно')
        if not re.findall(r'^[\w.\@\+\-]+', data['username']):
            raise serializers.ValidationError('Недопустимые символы в имени')
        if (User.objects.filter(email=data['email']).exists()
                and not User.objects.filter(username=data['username']).exists()):
            raise serializers.ValidationError('Email занят')
        if User.objects.filter(username=data['username']).exists():
            user = User.objects.get(username=data['username'])
            if user.email != data['email']:
                raise serializers.ValidationError('Email указан неверно')
        return data


class EmailVerificationSerializer(serializers.Serializer):
    """Serializer для верификации."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = '__all__'
