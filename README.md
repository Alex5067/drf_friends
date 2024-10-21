# DRF Friends API

Это API для социальной сети, реализованное на Django и Django REST Framework. Оно включает регистрацию пользователей, просмотр профиля, добавление в друзья, принятие и отклонение запросов, удаление друзей, Session и Token аутентификацию.

## Установка

### 1. Клонирование репозитория

```bash
git clone <URL-репозитория>
cd <название-проекта>
cd drf
touch .env
```
В .env нужно определить SECRET_KEY, DEBUG, GUNICORN_ADDRESS, GUNICORN_PORT параметры
• SECRET_KEY: Ключ, используемый Django для криптографических операций
•	DEBUG: Если установлено в True, Django будет выводить подробные ошибки, в производственной среде это значение должно быть установлено в False
•	GUNICORN_ADDRESS: Адрес, на котором Gunicorn будет слушать входящие запросы
•	GUNICORN_PORT: Порт, на котором Gunicorn будет принимать запросы

### 2. Запуск сервера

#### Через pip:

```bash
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
```

#### Через Docker:

```bash
docker-compose up -d
```

### 3. Доступ к API

После запуска сервер будет доступен по адресу: `http://127.0.0.1:8000/`

## API Endpoints

| URL                         | Метод | Описание                                      |
|-----------------------------|-------|-----------------------------------------------|
| `/admin/`                   | GET   | Панель администратора                         |
| `/api-auth/`                | GET   | Авторизация через DRF                         |
| `/register/`                | POST  | Регистрация нового пользователя               |
| `/accounts/profile/`        | GET   | Получение профиля текущего пользователя       |
| `/all_users/`               | GET   | Получение списка всех пользователей           |
| `/send_request_to/`         | POST  | Отправка запроса в друзья пользователю        |
| `/accept_request_from/`     | POST  | Принятие запроса в друзья от пользователя     |
| `/reject_request_from/`     | POST  | Отклонение запроса в друзья от пользователя   |
| `/delete_friend/`           | POST  | Удаление пользователя из друзей               |

## Примеры запросов

### 1. Регистрация пользователя

**URL:** `/register/`

**Метод:** `POST`

**Тело запроса:**

```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "testpassword"
}
```

### 2. Получение профиля текущего пользователя

**URL:** `/accounts/profile/`

**Метод:** `GET`

**Заголовки:**

```http
Authorization: Token <ваш токен>
```

### 3. Отправка запроса на добавление в друзья

**URL:** `/send_request_to/`

**Метод:** `POST`

**Заголовки:**

```http
Authorization: Token <ваш токен>
```

**Тело запроса:**

```json
{
  "username": "frienduser"
}
```

### 4. Принятие запроса в друзья

**URL:** `/accept_request_from/`

**Метод:** `POST`

**Заголовки:**

```http
Authorization: Token <ваш токен>
```

**Тело запроса:**

```json
{
  "username": "frienduser"
}
```

### 5. Отклонение запроса в друзья

**URL:** `/reject_request_from/`

**Метод:** `POST`

**Заголовки:**

```http
Authorization: Token <ваш токен>
```

**Тело запроса:**

```json
{
  "username": "frienduser"
}
```

### 6. Удаление друга

**URL:** `/delete_friend/`

**Метод:** `POST`

**Заголовки:**

```http
Authorization: Token <ваш токен>
```

**Тело запроса:**

```json
{
  "username": "frienduser"
}
```

## Тестирование

Для запуска тестов используйте команду из корневой директории проекта:

```bash
pytest
```

## Swagger UI и документация API

Swagger UI доступен по адресу `http://127.0.0.1:8000/swagger/`, а документация Redoc — по адресу `http://127.0.0.1:8000/redoc/`.
