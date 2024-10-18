import pytest
from friends.serializers import UserSerializer
from rest_framework.test import APIClient
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf.settings')
django.setup()

# Create your tests here.
@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    serializer = UserSerializer(data={"email": "test@mail.ru", "password": "password123", "username": "testuser"})
    if serializer.is_valid():
        return serializer.save()


@pytest.fixture
def create_second_user(db):
    serializer = UserSerializer(
        data={"email": "newuser@example.com", "password": "newpassword123", "username": "testuser2"}
    )
    if serializer.is_valid():
        return serializer.save()


def test_profile(api_client, create_user):
    response = api_client.post("/api-auth/login/", {"username": "testuser", "password": "password123"})

    # Проверяем, что логин успешен
    assert response.status_code == 302
    profile = api_client.get("/accounts/profile/")
    assert "testuser" == profile.data.get("username")
    assert "token" in profile.data


@pytest.mark.django_db
def test_register_user(api_client):
    params = {"username": "testuser2", "email": "newuser@example.com", "password": "newpassword123"}

    response = api_client.post("/register/", data=params)

    # Проверяем, что регистрация успешна
    assert response.status_code == 201
    assert response.data["username"] == "testuser2"
    assert "token" in response.data  # Проверяем, что токен был выдан

    api_client.login(username="testuser2", password="newpassword123")

    profile = api_client.get("/accounts/profile/")
    assert "testuser2" == profile.data.get("username")


def test_all_users(api_client, create_user, create_second_user):
    api_client.login(username="testuser2", password="newpassword123")

    response = api_client.get("/all_users/")

    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert len(response.data) > 0  # Отображается testuser пользователь


def test_send_friend_request_to(api_client, create_user, create_second_user):
    api_client.login(username="testuser", password="password123")

    params = {"username": "testuser2"}  # Пользователь, которому отправляем запрос
    response = api_client.post("/send_request_to/", data=params)

    assert response.status_code == 201
    assert response.data == f"Вы отправили заявку в друзья пользователю {params['username']}"

    profile = api_client.get("/accounts/profile/")
    friend_request_data = profile.data.get("friend_requests_sent")
    assert "testuser2" == friend_request_data[0]["to_user"]


def test_accept_friend_request(api_client, create_user, create_second_user):
    # Пользователи
    params = {"username": "testuser", "second_username": "testuser2"}

    # Авторизация testuser пользователя и отправка запроса testuser2
    api_client.login(username=params["username"], password="password123")
    send_to = api_client.post("/send_request_to/", data={"username": {params["second_username"]}})
    profile = api_client.get("/accounts/profile/")
    friends_sent = profile.data.get("friend_requests_sent", [])
    assert len(friends_sent) > 0
    assert send_to.data == f"Вы отправили заявку в друзья пользователю {params['second_username']}"

    # Авторизация testuser2 пользователя и принятие запроса testuser
    api_client.login(username=params["second_username"], password="newpassword123")
    profile = api_client.get("/accounts/profile/")
    friends_received = profile.data.get("friend_requests_received", [])
    assert len(friends_received) > 0

    accept_from = api_client.post("/accept_request_from/", data={"username": {params["username"]}})

    assert accept_from.data == f"Вы добавили {params['username']} в друзья"

    # Проверка на то, что при принятии запроса, происходит добавление в друзья
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
    # Пользователи
    params = {"username": "testuser", "second_username": "testuser2"}

    # Авторизация testuser пользователя и отправка запроса testuser2
    api_client.login(username=params["username"], password="password123")
    api_client.post("/send_request_to/", data={"username": {params["second_username"]}})

    # Авторизация testuser2 пользователя и отправка запроса testuser, отклонение заявки в друзья
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
    # Пользователи
    params = {"username": "testuser", "second_username": "testuser2"}

    # Авторизация testuser пользователя и отправка запроса testuser2
    api_client.login(username=params["username"], password="password123")
    api_client.post("/send_request_to/", data={"username": {params["second_username"]}})
    # Авторизация testuser2 пользователя и принятие запроса testuser
    api_client.login(username=params["second_username"], password="newpassword123")
    api_client.post("/accept_request_from/", data={"username": {params["username"]}})

    # Удаление друга, проверка списка друзей у обоих пользователей
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
    # Пользователи
    params = {"username": "testuser", "second_username": "testuser2"}

    # Авторизация testuser пользователя и отправка запроса testuser2
    api_client.login(username=params["username"], password="password123")
    api_client.post("/send_request_to/", data={"username": {params["second_username"]}})
    # Авторизация testuser2 пользователя и отправка запроса testuser, атоматическое добавление в друзья
    api_client.login(username=params["second_username"], password="newpassword123")
    api_client.post("/send_request_to/", data={"username": {params["username"]}})
    # Проверка на автоматическое добавление в друзья, если 2 пользователи отправили друг другу заявки
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
