from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment
from .notification_service import notification_service


@receiver(post_save, sender=Comment)
def comment_notification_handler(sender, instance, created, **kwargs):
    """Обработчик для отправки уведомлений при создании комментария."""
    if not created or instance.is_deleted:
        return

    if instance.parent:
        # Это ответ на комментарий
        notification_service.notify_reply_to_comment(instance)
    else:
        # Это комментарий к посту
        notification_service.notify_comment_on_post(instance)