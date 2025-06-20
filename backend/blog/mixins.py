from django.db import models
from django.utils import timezone

class TimestampMixin(models.Model):
    """Миксин для добавления временных меток создания и обновления."""
    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        verbose_name='Дата обновления'
    )

    class Meta:
        abstract = True