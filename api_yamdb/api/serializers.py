import re
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import EmailVerification, User


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        required=False
    )
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre',
                  'category', 'rating',
                  )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('id', 'pub_date',)


class ReviewSerializer(serializers.ModelSerializer):
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


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )

    def validate_email(self, value):
        if value in User.objects.values_list('email', flat=True):
            raise serializers.ValidationError('Указанный email используется')
        return value

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)
        lookup_field = 'username'


class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        max_length=254,
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
    )

    def validate(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError('Имя me недоступно')
        if not re.findall(r'^[\w.\@\+\-]+', data['username']):
            raise serializers.ValidationError('Недопустимые символы в имени')
        if (data['email'] in User.objects.values_list('email', flat=True)
           and data['username'] not in User.objects.values_list('username',
                                                                flat=True)):
            raise serializers.ValidationError('Email занят')
        if User.objects.filter(username=data['username']).exists():
            user = User.objects.get(username=data['username'])
            if user.email != data['email']:
                raise serializers.ValidationError('Email указан неверно')
        return data

    class Meta:
        model = User
        fields = ('username', 'email')


class EmailVerificationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = EmailVerification
        fields = '__all__'
