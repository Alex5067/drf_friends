from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.validators import UniqueValidator

from .models import Friend, FriendRequest


class FriendRequestSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели FriendRequest, представляющий запросы в друзья.

    Поля:
        from_user: Имя пользователя, отправившего запрос в друзья.
        to_user: Имя пользователя, получившего запрос в друзья.
        timestamp: Дата и время создания запроса.
    """

    from_user = serializers.CharField(source="from_user.username")
    to_user = serializers.CharField(source="to_user.username")

    class Meta:
        model = FriendRequest
        fields = ["from_user", "to_user", "timestamp"]


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и проверки данных пользователя.

    Поля:
        username: Имя пользователя (уникальное, обязательное).
        email: Электронная почта (уникальная, обязательная).
        password: Пароль пользователя (обязательный).
    """

    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Username is already taken")],
    )
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="Email is already in use")],
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def create(self, validated_data):
        """
        Создает нового пользователя с хэшированным паролем.

        Аргументы:
            validated_data: Данные, прошедшие проверку сериализатором.

        Возвращает:
            Объект пользователя.
        """
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
        )
        user.set_password(validated_data["password"])  # Хэшируем пароль
        user.save()
        return user


class FriendSerializer(serializers.ModelSerializer):
    """
    Сериализатор для представления информации о друзьях пользователя.

    Поля:
        username: Имя пользователя друга.
    """

    class Meta:
        model = User
        fields = ["username"]


class AllUsersSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения всех пользователей в системе.

    Поля:
        username: Имя пользователя.
    """

    class Meta:
        model = User
        fields = ["username"]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отображения профиля пользователя и его связанных данных, таких как друзья и заявки в друзья.

    Поля:
        username: Имя пользователя.
        email: Электронная почта пользователя.
        friends: Список друзей пользователя.
        friend_requests_sent: Список отправленных пользователем запросов в друзья.
        friend_requests_received: Список полученных пользователем запросов в друзья.
        token: Токен аутентификации пользователя.
    """

    friends = serializers.SerializerMethodField()
    friend_requests_sent = serializers.SerializerMethodField()
    friend_requests_received = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "friends",
            "friend_requests_sent",
            "friend_requests_received",
            "token",
        ]

    def get_friends(self, obj):
        """
        Возвращает список друзей пользователя.
        """
        friends = Friend.objects.filter(current_user=obj).prefetch_related("users")
        return FriendSerializer(friends.first().users.all(), many=True).data if friends.exists() else []

    def get_friend_requests_sent(self, obj):
        """
        Возвращает список запросов в друзья, отправленных пользователем.
        """
        sent_requests = FriendRequest.objects.filter(from_user=obj)
        return FriendRequestSerializer(sent_requests, many=True).data

    def get_friend_requests_received(self, obj):
        """
        Возвращает список запросов в друзья, полученных пользователем.
        """
        received_requests = FriendRequest.objects.filter(to_user=obj)
        return FriendRequestSerializer(received_requests, many=True).data

    def get_token(self, obj):
        """
        Возвращает токен аутентификации пользователя, если он существует.
        """
        try:
            token = Token.objects.get(user=obj)
            return token.key
        except Token.DoesNotExist:
            return None
