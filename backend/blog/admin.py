from django.contrib import admin
from django.db import models

from .models import Post, Comment, PostAttachment, CommentAttachment, CommentTree
from django.contrib import admin
from django.contrib.auth import get_user_model

from .notification_service import notification_service

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

class PostAttachmentInline(admin.TabularInline):
    """Инлайн для вложений к постам."""
    model = PostAttachment
    extra = 0
    readonly_fields = ('uploaded_at', 'file_type', 'thumbnail_preview')
    fields = ('file', 'file_type', 'uploaded_at', 'thumbnail_preview')
    verbose_name = 'Вложение'
    verbose_name_plural = 'Вложения'

    def thumbnail_preview(self, obj):
        """Превью миниатюры изображения."""
        if obj.thumbnail:
            return admin.utils.display.display_for_value(obj.thumbnail, empty_value_display='-')
        return '-'

    thumbnail_preview.short_description = 'Превью'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Админ-панель для управления постами."""
    list_display = ('title', 'author', 'created_at', 'is_published', 'comments_count')
    list_display_links = ('title',)
    readonly_fields = ('created_at', 'updated_at', 'comments_count')
    inlines = [PostAttachmentInline]
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('is_published', 'created_at', 'author')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    autocomplete_fields = ['author']

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'author', 'content', 'is_published')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at', 'comments_count'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Аннотируем количество комментариев."""
        return super().get_queryset(request).annotate(
            _comments_count=models.Count('comments', filter=models.Q(comments__is_deleted=False))
        )

    def comments_count(self, obj):
        """Отображаем количество комментариев."""
        return obj._comments_count

    comments_count.admin_order_field = '_comments_count'
    comments_count.short_description = 'Комментарии'

    actions = ['send_test_notification']

    def send_test_notification(self, request, queryset):
        """Отправить тестовое уведомление авторам выбранных постов."""
        count = 0
        for post in queryset:
            notification = notification_service.create_notification(
                notification_type='info',
                title='Тестовое уведомление',
                message=f'Это тестовое уведомление для поста "{post.title}"',
                user_id=post.author.id
            )
            notification_service.send_notification_to_user(post.author.id, notification)
            count += 1

        self.message_user(request, f'Отправлено {count} уведомлений')

    send_test_notification.short_description = 'Отправить тестовое уведомление авторам'


class CommentAttachmentInline(admin.TabularInline):
    """Инлайн для вложений к комментариям."""
    model = CommentAttachment
    extra = 0
    readonly_fields = ('uploaded_at', 'thumbnail_preview')
    fields = ('image', 'uploaded_at', 'thumbnail_preview')
    verbose_name = 'Изображение'
    verbose_name_plural = 'Изображения'

    def thumbnail_preview(self, obj):
        """Превью миниатюры изображения."""
        if obj.thumbnail:
            return admin.utils.display.display_for_value(obj.thumbnail, empty_value_display='-')
        return '-'

    thumbnail_preview.short_description = 'Превью'


class CommentTreeInline(admin.TabularInline):
    """Инлайн для дерева комментариев."""
    model = CommentTree
    extra = 0
    fk_name = 'comment'
    readonly_fields = ('depth',)
    fields = ('ancestor', 'depth')
    verbose_name = 'Связь в дереве'
    verbose_name_plural = 'Связи в дереве'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Админ-панель для управления комментариями."""
    list_display = ('get_short_content', 'author', 'post', 'parent', 'created_at', 'is_deleted', 'replies_count')
    list_display_links = ('get_short_content',)
    readonly_fields = ('created_at', 'updated_at', 'replies_count')
    inlines = [CommentAttachmentInline, CommentTreeInline]
    search_fields = ('content', 'author__username', 'post__title')
    list_filter = ('is_deleted', 'created_at', 'post')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    autocomplete_fields = ['author', 'post', 'parent']

    fieldsets = (
        ('Основная информация', {
            'fields': ('author', 'post', 'parent', 'content', 'is_deleted')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at', 'replies_count'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        """Аннотируем количество ответов."""
        return super().get_queryset(request).annotate(
            _replies_count=models.Count('replies', filter=models.Q(replies__is_deleted=False)))

    def replies_count(self, obj):
        """Отображаем количество ответов."""
        return obj._replies_count

    replies_count.admin_order_field = '_replies_count'
    replies_count.short_description = 'Ответы'

    def get_short_content(self, obj):
        """Возвращает сокращенное содержание комментария."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content

    get_short_content.short_description = 'Содержание'


@admin.register(CommentTree)
class CommentTreeAdmin(admin.ModelAdmin):
    """Админ-панель для дерева комментариев."""
    list_display = ('comment', 'ancestor', 'depth')
    list_display_links = ('comment',)
    readonly_fields = ('depth',)
    search_fields = ('comment__content', 'ancestor__content')
    list_filter = ('depth',)
    ordering = ('comment', 'depth')
    autocomplete_fields = ['comment', 'ancestor']


@admin.register(PostAttachment)
class PostAttachmentAdmin(admin.ModelAdmin):
    """Админ-панель для вложений к постам."""
    list_display = ('get_filename', 'post', 'file_type', 'uploaded_at', 'thumbnail_preview')
    list_display_links = ('get_filename',)
    readonly_fields = ('uploaded_at', 'file_type', 'thumbnail_preview')
    search_fields = ('post__title', 'file')
    list_filter = ('file_type', 'uploaded_at')
    date_hierarchy = 'uploaded_at'
    ordering = ('-uploaded_at',)
    autocomplete_fields = ['post']

    def thumbnail_preview(self, obj):
        """Превью миниатюры."""
        if obj.thumbnail:
            return admin.utils.display.display_for_value(obj.thumbnail, empty_value_display='-')
        return '-'

    thumbnail_preview.short_description = 'Превью'

    def get_filename(self, obj):
        """Возвращает имя файла."""
        return obj.file.name.split('/')[-1] if obj.file else 'Нет файла'

    get_filename.short_description = 'Имя файла'


@admin.register(CommentAttachment)
class CommentAttachmentAdmin(admin.ModelAdmin):
    """Админ-панель для вложений к комментариям."""
    list_display = ('get_filename', 'comment', 'uploaded_at', 'thumbnail_preview')
    list_display_links = ('get_filename',)
    readonly_fields = ('uploaded_at', 'thumbnail_preview')
    search_fields = ('comment__content', 'image')
    list_filter = ('uploaded_at',)
    date_hierarchy = 'uploaded_at'
    ordering = ('-uploaded_at',)
    autocomplete_fields = ['comment']

    def thumbnail_preview(self, obj):
        """Превью миниатюры."""
        if obj.thumbnail:
            return admin.utils.display.display_for_value(obj.thumbnail, empty_value_display='-')
        return '-'

    thumbnail_preview.short_description = 'Превью'

    def get_filename(self, obj):
        """Возвращает имя файла изображения."""
        return obj.image.name.split('/')[-1] if obj.image else 'Нет изображения'

    get_filename.short_description = 'Имя файла'