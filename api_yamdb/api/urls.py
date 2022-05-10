from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    UserViewSet,
    signup, get_token,
    TitlesViewSet,
    ReviewsViewSet,
    CommentViewSet,
    GenreViewSet,
    CategoryViewSet
)

app_name = 'api'


ver_1 = SimpleRouter('v1')
ver_1.register(r'users', UserViewSet, basename='users')
ver_1.register(r'titles', TitlesViewSet, basename='titles')
ver_1.register(
    r'titles/(?P<title_id>[0-9]+)/reviews',
    ReviewsViewSet,
    basename='reviews'
)
ver_1.register(
    r'titles/(?P<title_id>[0-9]+)/reviews/(?P<review_id>[0-9]+)/comments',
    CommentViewSet,
    basename='comments'
)
ver_1.register('categories', CategoryViewSet, basename='categories')
ver_1.register('genres', GenreViewSet, basename='genres')

ver_1_auth_patterns = [
    path('token/', get_token, name='token'),
    path('signup/', signup, name='signup'),
]
urlpatterns = [
    path('v1/', include(ver_1.urls)),
    path('v1/auth/', include(ver_1_auth_patterns)),
]
