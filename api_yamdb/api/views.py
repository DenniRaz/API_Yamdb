from http import HTTPStatus

from api.mixins import ListCreateDestroyViewSet
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, pagination, permissions, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title
from users.models import EmailVerification, User

from .mixins import ListCreateDestroyViewSet
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    CommentSerializer,
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
        Avg("reviews__score")
    ).order_by("name")
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return ReadOnlyTitleSerializer
        return TitleSerializer


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, pk=title_id)
        review = get_object_or_404(Review, pk=review_id, title=title.pk)
        comments = review.comments.all()
        return comments

    def perform_create(self, serializer):
        review_id = self.kwargs.get('review_id')
        serializer.save(author=self.request.user, review=review_id)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        review = title.reviews.all()
        return review

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        serializer.save(author=self.request.user, title=title_id)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("username",)
    lookup_field = "username"
    # дописать для me


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
        # генерация кода подтверждения
        confirmation_code = get_random_string(length=6)
        # отправка кода подтверждения на почту
        send_mail(
            'Confirmation code',
            f'Your confirmation code is: {confirmation_code}',
            'noreply@example.com',
            [email],
        )
        # запоминаем кому и какой мы направили код веривикации
        confirmation_obj, created = EmailVerification.objects.get_or_create(
            username=username)
        confirmation_obj.confirmation_code = confirmation_code
        # создаем пользователя, если его не было
        if username not in User.objects.values_list('username', flat=True):
            serializer.save()
        return Response(serializer.data, status=HTTPStatus.OK)
    return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)
