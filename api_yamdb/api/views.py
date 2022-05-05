from django.db.models import Avg
from rest_framework import viewsets, filters, mixins, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, action
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
    permission_classes = (IsAdminOrSuperuser, )
    lookup_field = "username"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(detail=False, methods=['GET', 'PATCH', 'DELETE'])
    def me(self, request, *args, **kwargs):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, username=request.user.username)
        if request.method == 'DELETE':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            if request.user.role == 'user':
                if serializer.is_valid():
                    serializer.save(role='user')
                    return Response(serializer.data, status=status.HTTP_200_OK)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'me':
            return (permissions.IsAuthenticated(),)
        return super().get_permissions()


@api_view(['POST'])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    if serializer.is_valid():
        code = random.randint(100000, 999999)
        email = request.data['email']
        send_mail(
            'Код подтверждения YaMDb',
            f'Ваш код подтверждения: {code}',
            'from@yamdb.com',
            [f'{email}'],
            fail_silently=False,
        )
        if request.data['username'] == 'me':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save(confirmation_code=code)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(User, username=request.data['username'])
        if request.data['confirmation_code'] == user.confirmation_code:
            token = RefreshToken.for_user(user)
            return Response({
                'username': request.data['username'],
                'token': str(token.access_token)
            })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
