from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from rest_framework.validators import UniqueValidator

from .models import Friend, FriendRequest

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.SerializerMethodField()
    to_user = serializers.SerializerMethodField()

    class Meta:
        model = FriendRequest
        fields = ["from_user", "to_user", "timestamp"]

    def get_from_user(self, obj):
        return obj.from_user.username

    def get_to_user(self, obj):
        return obj.to_user.username

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Username is already taken")]
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email is already in use")]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
        )
        user.set_password(validated_data['password'])  # Хэшируем пароль
        user.save()
        return user


class FriendSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username']


class AllUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class UserProfileSerializer(serializers.ModelSerializer):
    friends = serializers.SerializerMethodField()
    friend_requests_sent = serializers.SerializerMethodField()
    friend_requests_received = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'friends', 'friend_requests_sent', 'friend_requests_received', 'token']

    def get_friends(self, obj):
        friends = Friend.objects.filter(current_user=obj).prefetch_related('users')
        return FriendSerializer(friends.first().users.all(), many=True).data if friends.exists() else []

    def get_friend_requests_sent(self, obj):
        sent_requests = FriendRequest.objects.filter(from_user=obj)
        return FriendRequestSerializer(sent_requests, many=True).data

    def get_friend_requests_received(self, obj):
        received_requests = FriendRequest.objects.filter(to_user=obj)
        return FriendRequestSerializer(received_requests, many=True).data

    def get_token(self, obj):
        try:
            token = Token.objects.get(user=obj)
            return token.key
        except Token.DoesNotExist:
            return None
