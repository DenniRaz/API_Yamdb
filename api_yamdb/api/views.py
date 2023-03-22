from http import HTTPStatus

from api.mixins import ListCreateDestroyViewSet
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from reviews.models import Category, Genre, Review, Title
from users.models import EmailVerification, User

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
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(ListCreateDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).order_by('-id')
    pagination_class = pagination.PageNumberPagination
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitleSerializer
        return ReadOnlyTitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = pagination.PageNumberPagination
    permission_classes = (IsAuthorOrModeratorOrAdmin,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, pk=title_id)
        review = get_object_or_404(Review, pk=review_id, title=title.pk)
        comments = review.comments.all()
        return comments

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, pk=title_id)
        review = get_object_or_404(Review, pk=review_id, title=title.pk)
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(detail=False,
            methods=['GET', 'PATCH'],
            permission_classes=[permissions.IsAuthenticated, ])
    def me(self, request):
        me = get_object_or_404(User, username=request.user.username)
        serializer = UserSerializer(me, data=request.data, partial=True)
        if serializer.is_valid():
            # предотвращаем самостоятельное изменение роли юзером
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
        # генерация кода верификации
        confirmation_code = get_random_string(length=6)
        # отправка кода верификации на почту
        send_mail(
            'Confirmation code',
            f'Your confirmation code is: {confirmation_code}',
            'noreply@example.com',
            [email],
        )
        # запоминаем кому и какой мы направили код верификации
        confirmation_obj, created = EmailVerification.objects.get_or_create(
            username=username)
        confirmation_obj.confirmation_code = confirmation_code
        confirmation_obj.save()
        # создаем пользователя, если его не было
        if username not in User.objects.values_list('username', flat=True):
            serializer.save()
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
    if serializer.is_valid():
        data = serializer.validated_data
        user = get_object_or_404(User, username=data['username'])
        confirmation_obj = get_object_or_404(EmailVerification,
                                             username=data['username'])
        # проверка кода верификации ранее направленному на почту
        if data['confirmation_code'] == confirmation_obj.confirmation_code:
            # подставим в обект модели confirmation_obj иной confirmation_code,
            # чтобы полученным на почту кодом можно было воспользоваться раз
            confirmation_obj.confirmation_code = get_random_string(length=6)
            confirmation_obj.save()
            # создание access_token для пользователя
            token = RefreshToken.for_user(user).access_token
            return Response({'token': str(token)}, status=HTTPStatus.CREATED)
        return Response(
            {'confirmation_code': 'Неверный код верификации!'},
            status=HTTPStatus.BAD_REQUEST)
    return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
