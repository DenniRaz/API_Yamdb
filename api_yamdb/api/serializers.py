from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Comment, Review


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
        user = self.context['request'].user
        title_id = self.context['request'].parser_context['kwargs']['title_id']
        title = get_object_or_404(Title, pk=title_id)
        if Review.objects.filter(author=user, title=title).exists():
            raise serializers.ValidationError(
                'На одно произведение можно написать один отзыв!'
            )
        return attrs
