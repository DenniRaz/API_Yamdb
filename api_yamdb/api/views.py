from http import HTTPStatus

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, pagination, permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title

from users.models import User

from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import IsAdmin, IsAdminOrReadOnly, IsAuthorOrModeratorOrAdmin
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    EmailVerificationSerializer,
    GenreSerializer,
    ReadOnlyTitleSerializer,
    ReviewSerializer,
    SignUpSerializer,
    TitleSerializer,
    UserSerializer,
)


class CategoryViewSet(ListCreateDestroyViewSet):
    """ViewSet для категории."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenreViewSet(ListCreateDestroyViewSet):
    """ViewSet для жанра."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """ViewSet для произведения."""

    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('-id')
    pagination_class = pagination.PageNumberPagination
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitleSerializer
        return ReadOnlyTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet для отзыва."""

    serializer_class = ReviewSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (IsAuthorOrModeratorOrAdmin,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        review = title.reviews.all()
        return review

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментария."""

    serializer_class = CommentSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (IsAuthorOrModeratorOrAdmin,)

    def get_queryset(self):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        return review.comments.all()

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, pk=review_id)
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ('get', 'post', 'patch', 'delete')

    @action(detail=False,
            methods=['GET', 'PATCH'],
            permission_classes=[permissions.IsAuthenticated, ])
    def me(self, request):
        """Получение данных своей учётной записи."""
        me = request.user
        serializer = UserSerializer(me, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(role=me.role)
            return Response(serializer.data, status=HTTPStatus.OK)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def APISignUp(request):
    """
    Генерация и отправка кода подтверждения на почту.
    Создает пользователя, если его нет.
    """
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        username = serializer.validated_data['username']
        user, created = User.objects.get_or_create(username=username,
                                                   email=email)
        confirmation_code = default_token_generator.make_token(user)
        send_mail(
            'Confirmation code',
            f'Your confirmation code is: {confirmation_code}',
            'noreply@example.com',
            [email],
        )
        user.confirmation_code = confirmation_code
        user.save()
        return Response(serializer.data, status=HTTPStatus.OK)
    return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def GetJWTToken(request):
    """
    Генерация JWT-токена и отправка пользователю
    в обмен на username и confirmation code.
    """
    serializer = EmailVerificationSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        data = serializer.validated_data
        user = get_object_or_404(User, username=data['username'])
        if default_token_generator.check_token(user,
                                               data['confirmation_code']):
            user.confirmation_code = default_token_generator.make_token(user)
            user.save()
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)}, status=HTTPStatus.CREATED)
        return Response(
            {'confirmation_code': 'Неверный код верификации!'},
            status=HTTPStatus.BAD_REQUEST)
    return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
