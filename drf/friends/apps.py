from django.apps import AppConfig


class FriendsConfig(AppConfig):
    """
    Конфигурация приложения 'friends'.

    Поля:
        default_auto_field: Устанавливает тип автоматического поля для моделей по умолчанию (BigAutoField).
        name: Имя приложения.

    Методы:
        ready: Выполняется при готовности приложения.
        Импортирует сигналы для корректной работы сигналов внутри приложения.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "friends"

    def ready(self):
        """
        Метод, вызываемый при старте приложения для настройки сигналов.

        Импортирует модуль signals, который содержит логику обработки сигналов,
        таких как создание токенов для новых пользователей.
        """
        import friends.signals
