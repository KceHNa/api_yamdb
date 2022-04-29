from django.urls import path, include
from rest_framework.routers import SimpleRouter

from api.views import UserViewSet, signup, get_token

router = SimpleRouter()
router.register('users', UserViewSet)
urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/token/', get_token, name='token'),
    path('v1/auth/signup/', signup, name='signup'),
]
