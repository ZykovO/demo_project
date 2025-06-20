import os
from io import BytesIO

from PIL import Image
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

from blog.mixins import TimestampMixin
from blog.validators import validate_file_size, HTMLValidator


# Create your models here.
class Post(TimestampMixin, models.Model):
    """Модель поста блога."""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    content = models.TextField(
        verbose_name='Содержание',
        validators=[HTMLValidator()]
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Опубликован'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.title[:50]


class PostAttachment(models.Model):
    """Вложения к постам с обработкой изображений."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Пост'
    )
    file = models.FileField(
        upload_to='post_attachments/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'txt']),
            validate_file_size
        ],
        verbose_name='Файл'
    )
    file_type = models.CharField(
        max_length=10,
        editable=False,
        verbose_name='Тип файла'
    )
    thumbnail = models.ImageField(
        upload_to='post_thumbnails/',
        null=True,
        blank=True,
        verbose_name='Миниатюра'
    )
    uploaded_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name='Дата загрузки'
    )

    class Meta:
        verbose_name = 'Вложение к посту'
        verbose_name_plural = 'Вложения к постам'

    def save(self, *args, **kwargs):
        """Сохранение с определением типа файла и обработкой изображения."""
        self._set_file_type()
        super().save(*args, **kwargs)
        if self.is_image:
            self._process_image()

    def _set_file_type(self):
        """Определяет тип файла по расширению."""
        ext = os.path.splitext(self.file.name)[1][1:].lower()
        self.file_type = 'image' if ext in ['jpg', 'jpeg', 'png', 'gif'] else 'text'

    def _process_image(self):
        """Обрабатывает изображение: создает миниатюру 320x240."""
        if not self.file:
            return

        try:
            with Image.open(self.file.path) as img:
                # Проверяем, нужно ли изменять размер
                if img.width > 320 or img.height > 240:
                    # Создаем копию изображения для обработки
                    img_copy = img.copy()
                    # Пропорциональное изменение размера с сохранением соотношения сторон
                    img_copy.thumbnail((320, 240), Image.LANCZOS)
                    self._save_thumbnail(img_copy)
        except (IOError, OSError) as e:
            # Логируем ошибку, но не прерываем сохранение
            print(f'Ошибка обработки изображения: {str(e)}')

    def _save_thumbnail(self, img):
        """Сохраняет обработанную миниатюру."""
        thumb_io = BytesIO()
        # Определяем формат для сохранения
        format_name = 'JPEG'  # Используем JPEG по умолчанию
        if img.mode in ('RGBA', 'LA'):
            # Для изображений с прозрачностью используем PNG
            format_name = 'PNG'
        elif hasattr(img, 'format') and img.format:
            format_name = img.format

        img.save(thumb_io, format=format_name, quality=85)

        # Сохраняем миниатюру
        filename = os.path.basename(self.file.name)
        self.thumbnail.save(
            f'thumb_{filename}',
            ContentFile(thumb_io.getvalue()),
            save=False
        )

    @property
    def is_image(self):
        """Проверяет, является ли файл изображением."""
        return self.file_type == 'image'

    @property
    def is_text(self):
        """Проверяет, является ли файл текстовым."""
        return self.file_type == 'text'

    def __str__(self):
        return f'Вложение к посту "{self.post.title}"'


class Comment(TimestampMixin, models.Model):
    """Модель комментария с древовидной структурой."""
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост'
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies',
        verbose_name='Родительский комментарий'
    )
    content = models.TextField(
        verbose_name='Содержание',
        validators=[HTMLValidator()]
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Удален'
    )

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def save(self, *args, **kwargs):
        """Сохранение с обновлением дерева комментариев."""
        super().save(*args, **kwargs)
        self._update_comment_tree()

    def _update_comment_tree(self):
        """Поддерживает таблицу замыканий для иерархии комментариев."""
        # Удаляем существующие связи для данного комментария
        CommentTree.objects.filter(comment=self).delete()

        # Создаем самоссылку (глубина 0)
        CommentTree.objects.create(comment=self, ancestor=self, depth=0)

        # Если есть родительский комментарий
        if self.parent:
            # Получаем всех предков родителя и создаем новые связи
            for relation in CommentTree.objects.filter(comment=self.parent):
                CommentTree.objects.create(
                    comment=self,
                    ancestor=relation.ancestor,
                    depth=relation.depth + 1
                )

    def __str__(self):
        return f'Комментарий к "{self.post.title}" от {self.author}'


class CommentTree(models.Model):
    """Таблица замыканий для иерархии комментариев."""
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='descendants',
        verbose_name='Комментарий'
    )
    ancestor = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='ancestors',
        verbose_name='Предок'
    )
    depth = models.PositiveIntegerField(verbose_name='Глубина')

    class Meta:
        unique_together = ('comment', 'ancestor')
        verbose_name = 'Дерево комментариев'
        verbose_name_plural = 'Дерево комментариев'

    def __str__(self):
        return f'{self.comment} -> {self.ancestor} (глубина: {self.depth})'


class CommentAttachment(models.Model):
    """Вложения к комментариям (только изображения)."""
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Комментарий'
    )
    image = models.ImageField(
        upload_to='comment_attachments/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])],
        verbose_name='Изображение'
    )
    thumbnail = models.ImageField(
        upload_to='comment_thumbnails/',
        null=True,
        blank=True,
        verbose_name='Миниатюра'
    )
    uploaded_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name='Дата загрузки'
    )

    class Meta:
        verbose_name = 'Вложение к комментарию'
        verbose_name_plural = 'Вложения к комментариям'

    def save(self, *args, **kwargs):
        """Сохранение с обработкой изображения."""
        super().save(*args, **kwargs)
        self._process_image()

    def _process_image(self):
        """Обрабатывает изображение: создает миниатюру 320x240."""
        try:
            with Image.open(self.image) as img:
                # Проверяем, нужно ли изменять размер
                if img.width > 320 or img.height > 240:
                    # Пропорциональное изменение размера с сохранением соотношения сторон
                    img.thumbnail((320, 240), Image.LANCZOS)
                    self._save_thumbnail(img)
        except (IOError, OSError) as e:
            raise ValidationError(f'Ошибка обработки изображения: {str(e)}')

    def _save_thumbnail(self, img):
        """Сохраняет обработанную миниатюру."""
        thumb_io = BytesIO()
        # Определяем формат для сохранения
        format_name = img.format if img.format else 'JPEG'
        img.save(thumb_io, format=format_name, quality=85)

        # Сохраняем миниатюру
        self.thumbnail.save(
            f'thumb_{os.path.basename(self.image.name)}',
            ContentFile(thumb_io.getvalue()),
            save=False
        )
        super().save()

    def __str__(self):
        return f'Изображение к комментарию {self.comment.id}'
