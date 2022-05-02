from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (UserViewSet, signup, get_token, TitlesViewSet,
                    ReviewsViewSet, CommentViewSet,
                    GenreViewSet, CategoryViewSet)

app_name = 'api'


ver1 = SimpleRouter('v1')
ver1.register('users', UserViewSet)
ver1.register(r'titles', TitlesViewSet)
ver1.register(
    r'titles/(?P<title_id>[0-9]+)/reviews',
    ReviewsViewSet,
    basename='reviews'
)
ver1.register(
    r'titles/(?P<title_id>[0-9]+)/reviews/(?P<review_id>[0-9]+)/comments',
    CommentViewSet,
    basename='comments'
)
ver1.register('categories', CategoryViewSet)
ver1.register('genres', GenreViewSet)

urlpatterns = [
    path('v1/', include(ver1.urls)),
    path('v1/auth/token/', get_token, name='token'),
    path('v1/auth/signup/', signup, name='signup'),
]
