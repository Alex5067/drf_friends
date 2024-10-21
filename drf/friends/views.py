from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from friends.models import Friend, FriendRequest, User
from friends.serializers import (
    AllUsersSerializer,
    FriendSerializer,
    UserProfileSerializer,
    UserSerializer,
)
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

# Create your views here.


class Greetings(APIView):
    """
    Представление для отображения приветственного сообщения.
    Разрешен доступ для всех пользователей.
    """

    permission_classes = [permissions.AllowAny]
    renderer_classes = [StaticHTMLRenderer]

    def get(self, request):
        """
        Возвращает HTML-страницу с приветственным сообщением и ссылками на Swagger и ReDoc.

        :param request: HTTP-запрос.
        :return: Response с HTML-содержимым.
        """
        body = (
            "<html>"
            "<body style='padding: 10px;'>"
            "<h1>Welcome to the API</h1>"
            "<div>"
            "Check <a href='/swagger'>swagger</a>"
            " or <a href='/redoc'>redoc</a>"
            "</div>"
            "</body>"
            "</html>"
        )
        return Response(body)


class UserRegister(APIView):
    """
    Представление для регистрации нового пользователя.
    Разрешен доступ для всех пользователей.
    """

    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request, format=None):
        """
        Создает нового пользователя на основе переданных данных.
        Возвращает токен, имя пользователя и email при успешной регистрации.

        :param request: HTTP-запрос с данными пользователя (username, email, password).
        :param format: Формат данных.
        :return: Response с информацией о пользователе и токеном, либо ошибки валидации.
        """
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        serializer = UserSerializer(data={"email": email, "password": password, "username": username})
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {"username": user.username, "email": user.email, "token": token.key},
                status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class UserProfile(APIView):
    """
    Представление для получения профиля текущего пользователя.
    Доступ разрешен только аутентифицированным пользователям.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            200: "Username\nemail\ntoken",
            401: "Authentication credentials were not provided",
        },
    )
    def get(self, request, format=None):
        """
        Возвращает данные профиля текущего аутентифицированного пользователя.

        :param request: HTTP-запрос с токеном в заголовке.
        :param format: Формат данных.
        :return: Response с информацией о профиле пользователя.
        """
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllUsers(APIView):
    """
    Представление для получения списка всех пользователей, кроме текущего.
    Доступ разрешен только аутентифицированным пользователям.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={200: "Success", 401: "Authentication credentials were not provided"},
    )
    def get(self, request, format=None):
        """
        Возвращает список всех пользователей, кроме текущего пользователя.

        :param request: HTTP-запрос с токеном в заголовке.
        :param format: Формат данных.
        :return: Response с информацией о пользователях.
        """
        current_user = request.user
        users = User.objects.exclude(id=current_user.id)
        serializer = AllUsersSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendRequestToUser(APIView):
    """
    Представление для отправки заявки в друзья другому пользователю.
    Доступ разрешен только аутентифицированным пользователям.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя"),
            },
            required=["username"],
        ),
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            201: "Success",
            200: "Такая заявка уже существует",
        },
    )
    def post(self, request):
        """
        Отправляет заявку в друзья указанному пользователю.

        :param request: HTTP-запрос с токеном и username пользователя, которому отправляется заявка.
        :return: Response с результатом отправки заявки.
        """
        username = request.data.get("username")

        friend = get_object_or_404(User, username=username)

        friend_request = FriendRequest.objects.filter(from_user=request.user, to_user=friend).first()
        if request.user == friend:
            return Response(
                "Нельзя отправить заявку в друзья самому себе",
                status=status.HTTP_400_BAD_REQUEST,
            )

        is_friend = Friend.objects.filter(current_user=request.user, users=friend)

        if is_friend:
            return Response(f"{username} уже у вас в друзьях", status.HTTP_400_BAD_REQUEST)

        if not friend_request:
            reverse_request = FriendRequest.objects.filter(from_user=friend, to_user=request.user).first()
            if reverse_request:
                reverse_request.accept()
                reverse_request.delete()
                return Response(
                    f"Вы добавили в друзья пользователя {friend}",
                    status.HTTP_201_CREATED,
                )
            else:
                FriendRequest.objects.create(from_user=request.user, to_user=friend)
                return Response(
                    f"Вы отправили заявку в друзья пользователю {friend}",
                    status.HTTP_201_CREATED,
                )
        else:
            return Response("Такая заявка уже существует", status.HTTP_200_OK)


class AcceptRequestFromUser(APIView):
    """
    Представление для принятия заявки в друзья от другого пользователя.
    Доступ разрешен только аутентифицированным пользователям.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя"),
            },
            required=["username"],
        ),
        responses={201: "Вы добавили username в друзья"},
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def post(self, request):
        """
        Принимает заявку в друзья от указанного пользователя.

        :param request: HTTP-запрос с токеном и username пользователя, от которого пришла заявка.
        :return: Response с результатом принятия заявки.
        """
        username = request.data.get("username")

        friend = get_object_or_404(User, username=username)

        friend_request = FriendRequest.objects.filter(from_user=friend, to_user=request.user).first()
        if friend_request:
            friend_request.accept()
            friend_request.delete()
            return Response(f"Вы добавили {friend} в друзья", status.HTTP_201_CREATED)
        return Response(
            f"Не удалось принять запрос в друзья от {username}",
            status.HTTP_400_BAD_REQUEST,
        )


class RejectRequestFromUser(APIView):
    """
    Представление для отклонения заявки в друзья от другого пользователя.
    Доступ разрешен только аутентифицированным пользователям.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя"),
            },
            required=["username"],
        ),
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING,
            )
        ],
        responses={
            201: "Вы отклонили заявку username в друзья",
            400: "User or request doesn't exist",
        },
    )
    def post(self, request):
        """
        Отклоняет заявку в друзья от указанного пользователя.

        :param request: HTTP-запрос с токеном и username пользователя, от которого пришла заявка.
        :return: Response с результатом отклонения заявки.
        """
        username = request.data.get("username")

        friend = get_object_or_404(User, username=username)

        friend_request = FriendRequest.objects.filter(from_user=friend, to_user=request.user).first()
        if friend_request:
            friend_request.delete()
            return Response(f"Вы отклонили заявку в друзья от {friend}", status.HTTP_201_CREATED)
        return Response(f"Не удалось отклонить запрос от {username}", status.HTTP_400_BAD_REQUEST)


class DeleteFriend(APIView):
    """
    Представление для удаления пользователя из списка друзей.
    Доступ разрешен только аутентифицированным пользователям.
    """

    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING, description="Имя пользователя"),
            },
            required=[
                "username",
            ],
        ),
        responses={
            201: "Вы удалили username из друзей",
            400: "User doesn't exist or not a friend or user is yourself",
        },
        manual_parameters=[
            openapi.Parameter(
                "Authorization",
                openapi.IN_HEADER,
                description="Токен пользователя (формат: Token <ключ>)",
                type=openapi.TYPE_STRING,
            )
        ],
    )
    def post(self, request):
        """
        Удаляет указанного пользователя из списка друзей текущего пользователя.

        :param request: HTTP-запрос с токеном и username пользователя, которого необходимо удалить из друзей.
        :return: Response с результатом удаления из списка друзей.
        """
        username = request.data.get("username")
        current_user = request.user

        friend_to_lose = get_object_or_404(User, username=username)

        if username == str(current_user):
            return Response(f'{"Нельзя удалить самого себя из друзей"}', status.HTTP_400_BAD_REQUEST)

        friend_relation = Friend.objects.filter(current_user=current_user, users=friend_to_lose)
        if not friend_relation.exists():
            return Response(f"{username} не является вашим другом", status.HTTP_400_BAD_REQUEST)

        if friend_to_lose:
            Friend.lose_friend(current_user, friend_to_lose)
            Friend.lose_friend(friend_to_lose, current_user)
            return Response(f"Вы удалили {friend_to_lose} из друзей", status.HTTP_201_CREATED)
