import pytest
from friends.serializers import UserSerializer
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


# Create your tests here.
@pytest.fixture
def api_client():
    """
    Фикстура для создания экземпляра APIClient, который будет использоваться в тестах для отправки HTTP-запросов.
    """
    return APIClient()


@pytest.fixture
def create_user(db):
    """
    Фикстура для создания первого пользователя в базе данных.

    Возвращает:
        user: Экземпляр пользователя.
    """
    serializer = UserSerializer(
        data={
            "email": "test@mail.ru",
            "password": "password123",
            "username": "testuser",
        }
    )
    if serializer.is_valid():
        return serializer.save()


@pytest.fixture
def create_second_user(db):
    """
    Фикстура для создания второго пользователя в базе данных.

    Возвращает:
        user: Экземпляр второго пользователя.
    """
    serializer = UserSerializer(
        data={
            "email": "newuser@example.com",
            "password": "newpassword123",
            "username": "testuser2",
        }
    )
    if serializer.is_valid():
        return serializer.save()


def test_profile(api_client, create_user):
    """
    Тест проверяет, что при логине пользователя отображается его профиль.

    Шаги:
        1. Логин пользователя testuser.
        2. Получение профиля.
        3. Проверка имени пользователя и наличия токена.
    """
    response = api_client.post("/api-auth/login/", {"username": "testuser", "password": "password123"})

    assert response.status_code == 302
    profile = api_client.get("/accounts/profile/")
    assert "testuser" == profile.data.get("username")
    assert "token" in profile.data


@pytest.mark.django_db
def test_create_token_on_user_creation():
    """
    Тест проверяет, что при создании пользователя автоматически создается токен.

    Шаги:
        1. Создание пользователя.
        2. Проверка, что токен существует и его ключ является строкой.
    """
    User = get_user_model()

    user = User.objects.create_user(username="testuser", password="password123")

    token = Token.objects.get(user=user)
    assert token is not None
    assert isinstance(token.key, str)
    assert len(token.key) > 0


@pytest.mark.django_db
def test_register_user(api_client):
    """
    Тест проверяет успешную регистрацию пользователя.

    Шаги:
        1. Регистрация нового пользователя.
        2. Проверка, что регистрация успешна и токен был выдан.
        3. Проверка отображения профиля нового пользователя.
    """
    params = {
        "username": "testuser2",
        "email": "newuser@example.com",
        "password": "newpassword123",
    }

    response = api_client.post("/register/", data=params)

    assert response.status_code == 201
    assert response.data["username"] == "testuser2"
    assert "token" in response.data

    api_client.login(username="testuser2", password="newpassword123")

    profile = api_client.get("/accounts/profile/")
    assert "testuser2" == profile.data.get("username")


def test_all_users(api_client, create_user, create_second_user):
    """
    Тест проверяет, что отображается список всех пользователей.

    Шаги:
        1. Логин под вторым пользователем.
        2. Получение списка всех пользователей.
        3. Проверка, что список пользователей не пустой.
    """
    api_client.login(username="testuser2", password="newpassword123")

    response = api_client.get("/all_users/")

    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert len(response.data) > 0


def test_send_friend_request_to(api_client, create_user, create_second_user):
    """
    Тест отправки заявки в друзья.

    Шаги:
        1. Логин под первым пользователем.
        2. Отправка запроса в друзья второму пользователю.
        3. Проверка, что запрос был отправлен.
    """
    api_client.login(username="testuser", password="password123")

    params = {"username": "testuser2"}
    response = api_client.post("/send_request_to/", data=params)

    assert response.status_code == 201
    assert response.data == f"Вы отправили заявку в друзья пользователю {params['username']}"

    profile = api_client.get("/accounts/profile/")
    friend_request_data = profile.data.get("friend_requests_sent")
    assert "testuser2" == friend_request_data[0]["to_user"]


def test_accept_friend_request(api_client, create_user, create_second_user):
    """
    Тест принятия заявки в друзья.

    Шаги:
        1. Первый пользователь отправляет запрос в друзья второму.
        2. Второй пользователь принимает запрос.
        3. Проверка, что пользователи стали друзьями.
    """
    params = {"username": "testuser", "second_username": "testuser2"}

    api_client.login(username=params["username"], password="password123")
    send_to = api_client.post("/send_request_to/", data={"username": {params["second_username"]}})
    profile = api_client.get("/accounts/profile/")
    friends_sent = profile.data.get("friend_requests_sent", [])
    assert len(friends_sent) > 0
    assert send_to.data == f"Вы отправили заявку в друзья пользователю {params['second_username']}"

    api_client.login(username=params["second_username"], password="newpassword123")
    profile = api_client.get("/accounts/profile/")
    friends_received = profile.data.get("friend_requests_received", [])
    assert len(friends_received) > 0

    accept_from = api_client.post("/accept_request_from/", data={"username": {params["username"]}})

    assert accept_from.data == f"Вы добавили {params['username']} в друзья"

    profile = api_client.get("/accounts/profile/")
    friends = profile.data.get("friends", [])
    friend_usernames = [friend["username"] for friend in friends]
    assert params["username"] in friend_usernames

    api_client.login(username=params["username"], password="password123")
    profile = api_client.get("/accounts/profile/")
    friends = profile.data.get("friends", [])
    friend_usernames = [friend["username"] for friend in friends]
    assert params["second_username"] in friend_usernames


def test_reject_friend_request(api_client, create_user, create_second_user):
    """
    Тест отклонения заявки в друзья.

    Шаги:
        1. Первый пользователь отправляет запрос в друзья второму.
        2. Второй пользователь отклоняет запрос.
        3. Проверка, что заявка была отклонена.
    """
    params = {"username": "testuser", "second_username": "testuser2"}

    api_client.login(username=params["username"], password="password123")
    api_client.post("/send_request_to/", data={"username": {params["second_username"]}})

    api_client.login(username=params["second_username"], password="newpassword123")
    profile = api_client.get("/accounts/profile/")
    friend_request_data = profile.data.get("friend_requests_received")
    assert len(friend_request_data) == 1

    accept_from = api_client.post("/reject_request_from/", data={"username": {params["username"]}})
    assert accept_from.data == f"Вы отклонили заявку в друзья от {params['username']}"
    profile = api_client.get("/accounts/profile/")
    friend_request_data = profile.data.get("friend_requests_received")
    assert len(friend_request_data) < 1


def test_delete_friend(api_client, create_user, create_second_user):
    """
    Тест удаления друга.

    Шаги:
        1. Первый пользователь отправляет запрос в друзья второму.
        2. Второй пользователь принимает запрос.
        3. Первый пользователь удаляет второго из друзей.
        4. Проверка, что список друзей у обоих пользователей пуст.
    """
    params = {"username": "testuser", "second_username": "testuser2"}

    api_client.login(username=params["username"], password="password123")
    api_client.post("/send_request_to/", data={"username": {params["second_username"]}})
    api_client.login(username=params["second_username"], password="newpassword123")
    api_client.post("/accept_request_from/", data={"username": {params["username"]}})

    response = api_client.post("/delete_friend/", data={"username": {params["username"]}})
    assert response.data == f"Вы удалили {params['username']} из друзей"
    profile = api_client.get("/accounts/profile/")
    friends = profile.data.get("friends")
    assert len(friends) < 1

    api_client.login(username=params["username"], password="password123")
    profile = api_client.get("/accounts/profile/")
    friends = profile.data.get("friends")
    assert len(friends) < 1


def test_auto_add_to_friend(api_client, create_user, create_second_user):
    """
    Тест автоматического добавления в друзья, если оба пользователя отправили запросы друг другу.

    Шаги:
        1. Первый пользователь отправляет запрос в друзья второму.
        2. Второй пользователь отправляет запрос первому.
        3. Проверка, что оба пользователя автоматически стали друзьями.
    """
    params = {"username": "testuser", "second_username": "testuser2"}

    api_client.login(username=params["username"], password="password123")
    api_client.post("/send_request_to/", data={"username": {params["second_username"]}})
    api_client.login(username=params["second_username"], password="newpassword123")
    api_client.post("/send_request_to/", data={"username": {params["username"]}})
    profile = api_client.get("/accounts/profile/")
    friends = profile.data.get("friends")
    friends_request = profile.data.get("friend_requests_sent")
    assert len(friends_request) < 1
    assert len(friends) > 0

    api_client.login(username=params["username"], password="password123")
    profile = api_client.get("/accounts/profile/")
    friends = profile.data.get("friends")
    friends_request = profile.data.get("friend_requests_sent")
    assert len(friends_request) < 1
    assert len(friends) > 0


def test_if_already_friends(api_client, create_user, create_second_user):
    """
    Тест невозможности отправки заявки, если пользователи уже являются друзьями.

    Шаги:
        1. Оба пользователя отправляют друг другу заявки в друзья.
        2. Проверка, что пользователи автоматически стали друзьями.
        3. Проверка, что повторная отправка заявки невозможна.
    """
    params = {"username": "testuser", "second_username": "testuser2"}

    api_client.login(username=params["username"], password="password123")
    api_client.post("/send_request_to/", data={"username": {params["second_username"]}})
    api_client.login(username=params["second_username"], password="newpassword123")
    api_client.post("/send_request_to/", data={"username": {params["username"]}})
    profile = api_client.get("/accounts/profile/")
    friends = profile.data.get("friends")
    friends_request = profile.data.get("friend_requests_sent")
    assert len(friends_request) < 1
    assert len(friends) > 0

    api_client.login(username=params["username"], password="password123")
    profile = api_client.get("/accounts/profile/")
    friends = profile.data.get("friends")
    friends_request = profile.data.get("friend_requests_sent")
    assert len(friends_request) < 1
    assert len(friends) > 0

    req = api_client.post("/send_request_to/", data={"username": {params["second_username"]}})
    profile = api_client.get("/accounts/profile/")
    friends_request = profile.data.get("friend_requests_sent")
    assert req.data == f"{params['second_username']} уже у вас в друзьях"
    assert len(friends_request) < 1
