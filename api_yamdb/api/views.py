from django.db.models import Avg
from rest_framework import viewsets, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
import random
from django.core.mail import send_mail

from reviews.models import User, Title, Review, Comment
from .serializers import (UserSerializer, SignUpSerializer,
                          GetTokenSerializer, ReviewSerializer,
                          TitleSerializer, CommentSerializer)


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


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    # queryset = Title.objects.all().annotate(
    #     Avg("reviews__score")
    # ).order_by("name")
    serializer_class = TitleSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment
    serializer_class = CommentSerializer

    def get_queryset(self):
        # Получаем id произведения и id отзыва на него
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        title = get_object_or_404(Title, pk=title_id)
        reviews = title.reviews.all()
        return reviews

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)