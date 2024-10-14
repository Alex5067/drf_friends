from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics
from friends.models import Friend, User
from friends.models import FriendRequest
from rest_framework import permissions
from friends.serializers import FriendSerializer, UserSerializer, UserProfileSerializer, AllUsersSerializer
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg import openapi
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

# Create your views here.

class UserRegister(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request, format=None):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        serializer = UserSerializer(data={'email': email, 'password': password, 'username': username})
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'username': user.username,
                'email': user.email,
                'token': token.key
            }, status.HTTP_201_CREATED)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class UserProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: "Username\nemail\ntoken",
            401: "Authentication credentials were not provided"
        }
    )
    def get(self, request, format=None):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AllUsers(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={
            200: "Success",
            401: "Authentication credentials were not provided"
        }
    )
    def get(self, request, format=None):
        current_user = request.user
        users = User.objects.exclude(id=current_user.id)
        serializer = AllUsersSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SendRequestToUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),},
            required=['username']),
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={201: "Success", 200: "Такая заявка уже существует",})
    def post(self, request):
        username = request.data.get('username')

        try:
            friend = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response(f"Пользователя с никнеймом {username} не существует", status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.filter(from_user=request.user, to_user=friend).first()
        if request.user == friend:
            return Response("Нельзя отправить заявку в друзья себе", status=status.HTTP_400_BAD_REQUEST)

        if not friend_request:
            reverse_request = FriendRequest.objects.filter(from_user=friend, to_user=request.user).first()
            if reverse_request:
                reverse_request.accept()
                reverse_request.delete()
                return Response(f"Вы добавили в друзья пользователя {friend}", status.HTTP_201_CREATED)
            else:
                FriendRequest.objects.create(from_user=request.user, to_user=friend)
                return Response(f"Вы отправили заявку в друзья пользователю {friend}", status.HTTP_201_CREATED)
        else:
            return Response("Такая заявка уже существует", status.HTTP_200_OK)

class AcceptRequestFromUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),},
            required=['username']), responses={201: "Вы добавили username в друзья"},
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING
                )
            ],
        )
    def post(self, request):
        username = request.data.get('username')

        try:
            friend = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response(f"Пользователя с никнеймом {username} не существует", status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.filter(from_user=friend, to_user=request.user).first()
        if friend_request:
            friend_request.accept()
            friend_request.delete()
            return Response(f"Вы добавили {friend} в друзья", status.HTTP_201_CREATED)
        return Response(f"Не удалось принять запрос в друзья от {username}", status.HTTP_400_BAD_REQUEST)

class RejectRequestFromUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),},
            required=['username']),
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={201: "Вы отклонили заявку username в друзья", 400: "User or request doesn't exist"})
    def post(self, request):
        username = request.data.get('username')

        try:
            friend = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response(f"Пользователя с никнеймом {username} не существует", status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest.objects.filter(from_user=friend, to_user=request.user).first()
        if friend_request:
            friend_request.delete()
            return Response(f"Вы отклонили заявку в друзья от {friend}", status.HTTP_201_CREATED)
        return Response(f"Не удалось отклонить запрос от {username}", status.HTTP_400_BAD_REQUEST)

class DeleteFriend(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),},
            required=['username',]), responses={201: "Вы удалили username из друзей",
                                                400: "User doesn't exist or not a friend or user is yourself"},
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING
                )
            ],
        )
    def post(self, request):
        username = request.data.get('username')
        current_user = request.user

        try:
            friend_to_lose = User.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response(f"Пользователя с никнеймом {username} не существует", status.HTTP_400_BAD_REQUEST)

        if username == str(current_user):
            return Response(f"Нельзя удалить самого себя из друзей", status.HTTP_400_BAD_REQUEST)

        friend_relation = Friend.objects.filter(current_user=current_user, users=friend_to_lose)
        if not friend_relation.exists():
            return Response(f"{username} не является вашим другом", status.HTTP_400_BAD_REQUEST)

        if friend_to_lose:
            Friend.lose_friend(current_user, friend_to_lose)
            Friend.lose_friend(friend_to_lose, current_user)
            return Response(f"Вы удалили {friend_to_lose} из друзей", status.HTTP_201_CREATED)
