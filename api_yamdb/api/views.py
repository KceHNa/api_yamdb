import random

from django.db.models import Avg
from rest_framework import viewsets, filters, status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import User, Title, Genre, Category, Review
from .filters import TitleFilter
from .permissions import (
    IsAuthorAndStaffOrReadOnly,
    IsAdminOrSuperuser,
    AnyReadOnly,
    AdminOrReadOnly,
)
from .serializers import (
    UserSerializer,
    SignUpSerializer,
    GetTokenSerializer,
    ReviewSerializer,
    TitleSerializer,
    CommentSerializer,
    GenreSerializer,
    CategorySerializer,
    TitlePostSerializer
)
from .mixins import CreateListDestroy
from django.conf import settings


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrSuperuser, )
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=[permissions.IsAuthenticated, ]
    )
    def me(self, request, *args, **kwargs):
        user = request.user
        if request.method == 'GET':
            serializer = UserSerializer(user)
            return Response(serializer.data)
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def signup(request):
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    code = random.randint(100000, 999999)
    email = request.data['email']
    send_mail(
        'Код подтверждения YaMDb',
        f'Ваш код подтверждения: {code}',
        settings.CREW_EMAIL,
        [f'{email}'],
        fail_silently=False,
    )
    serializer.save(confirmation_code=code)
    return Response(serializer.data)


@api_view(['POST'])
def get_token(request):
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = get_object_or_404(User, username=request.data['username'])
    token = RefreshToken.for_user(user)
    return Response({
        'username': request.data['username'],
        'token': str(token.access_token)
    })


class GenreViewSet(CreateListDestroy):
    search_fields = ('name',)
    lookup_field = 'slug'
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (IsAdminOrSuperuser,)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return AnyReadOnly(),
        return super().get_permissions()


class CategoryViewSet(CreateListDestroy):
    search_fields = ('name',)
    lookup_field = 'slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (filters.SearchFilter,)
    permission_classes = (AdminOrReadOnly,)


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        Avg('reviews__score')
    ).order_by('name')
    serializer_class = TitleSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = TitleFilter
    permission_classes = (AdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TitlePostSerializer
        return TitleSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthorAndStaffOrReadOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if serializer.is_valid:
            serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorAndStaffOrReadOnly]

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review, title_id=title_id, id=review_id
        )
        return review.comments.all().order_by('id')

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(
            Review, title_id=title_id, id=review_id
        )
        user = get_object_or_404(User, username=self.request.user)
        serializer.save(author=user, review=review)
