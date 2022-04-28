from rest_framework import serializers
from django.shortcuts import get_object_or_404

from .models import User


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
        fields = ('token',)

    def get_token(self, obj):
        #user = get_object_or_404(User, username=obj.name)
        #refresh = RefreshToken.for_user(user)
        #return str(refresh)
        return obj
