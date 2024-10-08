from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)  # True - открыта, False - закрыта

    def accept(self):
        # Добавляем друг друга в друзья
        friend, created = Friend.objects.get_or_create(current_user=self.from_user)
        friend.users.add(self.to_user)
        friend, created = Friend.objects.get_or_create(current_user=self.to_user)
        friend.users.add(self.from_user)
        # Закрываем заявку
        self.status = True
        self.save()

    def decline(self):
        # Отклоняем заявку
        self.status = False
        self.save()

    def delete(self):
        # Удаляем заявку
        super().delete()

class Friend(models.Model):
    users = models.ManyToManyField(User)
    current_user = models.ForeignKey(User, related_name='owner', null=True, on_delete=models.CASCADE)

    @classmethod
    def make_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.add(new_friend)

    @classmethod
    def lose_friend(cls, current_user, new_friend):
        friend, created = cls.objects.get_or_create(
            current_user=current_user
        )
        friend.users.remove(new_friend)