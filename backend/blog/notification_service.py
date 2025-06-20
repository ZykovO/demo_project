import json
import uuid
from datetime import datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Comment, Post


class NotificationService:
    """Сервис для отправки уведомлений."""

    def __init__(self):
        self.channel_layer = get_channel_layer()

    def create_notification(self, notification_type, title, message, user_id):
        """Создает уведомление."""
        return {
            'id': str(uuid.uuid4()),
            'type': notification_type,
            'title': title,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'read': False
        }

    def send_notification_to_user(self, user_id, notification):
        """Отправляет уведомление конкретному пользователю."""
        if self.channel_layer:
            async_to_sync(self.channel_layer.group_send)(
                f"user_{user_id}",
                {
                    'type': 'notification_message',
                    'notification': notification
                }
            )

    def notify_comment_on_post(self, comment):
        """Уведомление о новом комментарии к посту."""
        post_author = comment.post.author

        # Не уведомляем автора о собственных комментариях
        if post_author.id == comment.author.id:
            return

        notification = self.create_notification(
            notification_type='info',
            title='Новый комментарий',
            message=f'{comment.author.username} оставил комментарий к вашему посту "{comment.post.title}"',
            user_id=post_author.id
        )

        self.send_notification_to_user(post_author.id, notification)

    def notify_reply_to_comment(self, reply):
        """Уведомление о ответе на комментарий."""
        if not reply.parent:
            return

        parent_author = reply.parent.author

        # Не уведомляем автора о собственных ответах
        if parent_author.id == reply.author.id:
            return

        notification = self.create_notification(
            notification_type='info',
            title='Ответ на комментарий',
            message=f'{reply.author.username} ответил на ваш комментарий в посте "{reply.post.title}"',
            user_id=parent_author.id
        )

        self.send_notification_to_user(parent_author.id, notification)


# Создаем глобальный экземпляр сервиса
notification_service = NotificationService()