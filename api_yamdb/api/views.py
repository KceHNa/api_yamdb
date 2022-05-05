from django.db.models import Avg
from rest_framework import viewsets, permissions, filters, mixins
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
import random
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import User, Title, Genre, Category

from .filters import TitleFilter
from .permissions import IsAuthorAndStaffOrReadOnly, IsAdminOrSuperuser
from .serializers import (UserSerializer, SignUpSerializer,
                          GetTokenSerializer, ReviewSerializer,
                          TitleSerializer, CommentSerializer,
                          GenreSerializer, CategorySerializer)


class CreateListDestroy(mixins.CreateModelMixin,
                        mixins.DestroyModelMixin,
                        mixins.ListModelMixin,
                        viewsets.GenericViewSet):

    pass


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


class GenreViewSet(CreateListDestroy):
    search_fields = ('name',)
    lookup_field = 'slug'
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)

    def get_permissions(self):
        if self.action == 'list':
            return IsAdminOrSuperuser()


class CategoryViewSet(CreateListDestroy):
    search_fields = ('name',)
    lookup_field = 'slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)

    def get_permissions(self):
        if self.action == 'list':
            return IsAdminOrSuperuser()


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rank=Avg('reviews__score')).all()
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = TitleFilter

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return IsAdminOrSuperuser()


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permissions_classes = [IsAuthorAndStaffOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permissions_classes = [IsAuthorAndStaffOrReadOnly]

    def get_queryset(self):
        # Получаем id произведения и id отзыва на него
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        try:
            review_id = self.kwargs.get('review_id')
            review = title.reviews.get(id=review_id)
        except TypeError:
            TypeError('Нет такого отзыва по этому id')
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        try:
            review_id = self.kwargs.get('review_id')
            review = title.reviews.get(id=review_id)
        except TypeError:
            TypeError('Нет такого отзыва по этому id')
        serializer.save(author=self.request.user, review=review)
