from django.db.models import Avg
from django.shortcuts import get_object_or_404
from reviews.models import Category, Genre, Title, Review
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleSerializer, ReadOnlyTitleSerializer,
                          CommentSerializer, ReviewSerializer)
from .permissions import IsAdminOrReadOnly
from api.mixins import ListCreateDestroyViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework import pagination


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
