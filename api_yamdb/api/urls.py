from api.views import CommentViewSet, ReviewViewSet

from django.urls import include, path

from rest_framework import routers

router = routers.DefaultRouter()
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments',
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews',
)

urlpatterns = [
    path('v1/', include(router.urls)),
]
