from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    Сигнал для автоматического создания токена аутентификации для нового пользователя.

    Этот сигнал вызывается при сохранении объекта модели пользователя (`AUTH_USER_MODEL`).
    Если пользователь был создан (флаг `created=True`), для него создается новый токен аутентификации.

    :param sender: Модель, которая отправляет сигнал (в данном случае `AUTH_USER_MODEL`).
    :param instance: Экземпляр модели пользователя, который был создан или изменен.
    :param created: Логическое значение, указывающее, был ли пользователь создан (True) или обновлен (False).
    :param kwargs: Дополнительные аргументы, передаваемые сигналу.

    Если пользователь был создан, генерируется и сохраняется новый токен аутентификации для данного пользователя.
    """
    if instance and created:
        Token.objects.create(user=instance)
