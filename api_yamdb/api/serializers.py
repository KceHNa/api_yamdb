from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import User, Title, Review, Comment, Category, Genre


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = User


class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username')


class GetTokenSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code', 'token')


class TitleSerializer(serializers.ModelSerializer):
    rank = serializers.IntegerField(
        source='reviews__score__avg',
        read_only=True
    )
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    description = serializers.CharField(required=False)

    class Meta:
        fields = '__all__'
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault(),
        slug_field='username'
    )

    def validate_user_reviews(self, data):
        # Id произведения из контекса,
        title_id = self.context['view'].kwargs.get('title_id')
        user = self.context.get('request').user
        if user.reviews.filter(title_id=title_id).exists():
            raise serializers.ValidationError(
                'Возможено добавить только один отзыв!'
            )
        return data

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'
