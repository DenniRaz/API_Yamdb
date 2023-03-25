from django.urls import path, include
from .views import (
    APISignUp,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    GetJWTToken,
    ReviewViewSet,
    TitleViewSet,
    UserViewSet,
)
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
router.register(
    r'users',
    UserViewSet,
    basename='users',
)
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)

auth_urlpatterns = [
    path('signup/', APISignUp),
    path('token/', GetJWTToken),
]

urlpatterns = [
    path('v1/auth/', include(auth_urlpatterns)),
    path('v1/', include(router.urls)),
]
