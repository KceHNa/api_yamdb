from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import LimitOffsetPagination
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
import random

from .models import User
from .serializers import (
    UserSerializer,
    SignUpSerializer,
    GetTokenSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(['POST'])
def signup(request):
    print(request.data['username'])
    code = random.randint(100000, 999999)
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(confirmation_code=code)
    return Response(serializer.data)



@api_view(['POST'])
def get_token(request):
    user = get_object_or_404(User, username=request.data['username'])
    serializer = GetTokenSerializer(data=request.data)
    if serializer.is_valid():
        pass#serializer.save(user=user)
        if request.data['confirmation_code'] == user.confirmation_code:
            print('успех')
    return Response(serializer.data)
