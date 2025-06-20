from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from blog.notification_service import notification_service

User = get_user_model()


class Command(BaseCommand):
    help = 'Отправить тестовое уведомление пользователю'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='ID пользователя')
        parser.add_argument('--type', default='info', choices=['info', 'success', 'warning', 'error'])
        parser.add_argument('--title', required=True, help='Заголовок уведомления')
        parser.add_argument('--message', required=True, help='Текст уведомления')

    def handle(self, *args, **options):
        try:
            user = User.objects.get(id=options['user_id'])

            notification = notification_service.create_notification(
                notification_type=options['type'],
                title=options['title'],
                message=options['message'],
                user_id=user.id
            )

            notification_service.send_notification_to_user(user.id, notification)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Уведомление отправлено пользователю {user.username} (ID: {user.id})'
                )
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Пользователь с ID {options["user_id"]} не найден')
            )
