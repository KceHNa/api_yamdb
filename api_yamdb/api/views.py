from rest_framework import viewsets, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
import random
from django.core.mail import send_mail

from reviews.models import User
from .serializers import (
    UserSerializer,
    SignUpSerializer,
    GetTokenSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)


@api_view(['POST'])
def signup(request):
    code = random.randint(100000, 999999)
    email = request.data['email']
    send_mail(
        'Код подтверждения YaMDb',
        f'Ваш код подтверждения: {code}',
        'from@yamdb.com',
        [f'{email}'],
        fail_silently=False,
    )
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(confirmation_code=code)
    return Response(serializer.data)


@api_view(['POST'])
def get_token(request):
    user = get_object_or_404(User, username=request.data['username'])
    serializer = GetTokenSerializer(data=request.data)
    if serializer.is_valid():
        pass
    if request.data['confirmation_code'] == user.confirmation_code:
        token = RefreshToken.for_user(user)
        return Response({
            'username': request.data['username'],
            'token': str(token.access_token)
        })
    return Response(serializer.data)
