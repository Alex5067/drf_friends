from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class FriendRequest(models.Model):
    """
    Модель для представления запроса на добавление в друзья между двумя пользователями.

    Поля:
        from_user: Пользователь, отправивший запрос в друзья.
        to_user: Пользователь, получивший запрос в друзья.
        timestamp: Дата и время создания запроса.

    Методы:
        accept: Принимает запрос в друзья, добавляя пользователей друг другу в список друзей.
    """

    from_user = models.ForeignKey(User, related_name="friend_requests_sent", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="friend_requests_received", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def accept(self):
        """
        Принимает запрос в друзья и добавляет пользователей друг другу в список друзей.

        Этот метод создает или обновляет объект Friend для обоих пользователей, добавляя их друг к другу в друзья.
        """
        friend, created = Friend.objects.get_or_create(current_user=self.from_user)
        friend.users.add(self.to_user)
        friend, created = Friend.objects.get_or_create(current_user=self.to_user)
        friend.users.add(self.from_user)
        self.save()


class Friend(models.Model):
    """
    Модель для представления списка друзей пользователя.

    Поля:
        users: Список друзей пользователя.
        current_user: Пользователь, владеющий данным списком друзей.

    Методы:
        lose_friend: Удаляет указанного друга из списка друзей текущего пользователя.
    """

    users = models.ManyToManyField(User)
    current_user = models.ForeignKey(User, related_name="owner", null=True, on_delete=models.CASCADE)

    @classmethod
    def lose_friend(cls, current_user, new_friend):
        """
        Удаляет указанного пользователя из списка друзей текущего пользователя.

        Аргументы:
                current_user: Пользователь, который теряет друга.
                new_friend: Пользователь, которого нужно удалить из списка друзей.
        """
        friend, created = cls.objects.get_or_create(current_user=current_user)
        friend.users.remove(new_friend)
