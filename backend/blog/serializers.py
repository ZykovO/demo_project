from rest_framework import serializers
from .models import Post, PostAttachment, Comment, CommentAttachment, CommentTree
from .validators import HTMLValidator
from drf_yasg.utils import swagger_serializer_method


class PostAttachmentSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения вложений к постам."""
    file_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = PostAttachment
        fields = ['id', 'file_type', 'file_url', 'thumbnail_url', 'uploaded_at']
        read_only_fields = fields

    @swagger_serializer_method(serializer_or_field=serializers.URLField)
    def get_file_url(self, obj):
        """Возвращает URL файла."""
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else None

    @swagger_serializer_method(serializer_or_field=serializers.URLField)
    def get_thumbnail_url(self, obj):
        """Возвращает URL миниатюры."""
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return obj.thumbnail.url if obj.thumbnail else None


class PostAttachmentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания вложений к постам."""

    class Meta:
        model = PostAttachment
        fields = ['file']
        extra_kwargs = {
            'file': {
                'help_text': 'Файл для загрузки (jpg, jpeg, png, gif, txt), макс. 100KB'
            }
        }

    def validate_file(self, value):
        """Дополнительная валидация файла."""
        if value.size > 100 * 1024:  # 100 КБ
            raise serializers.ValidationError('Размер файла не должен превышать 100 КБ.')

        ext = value.name.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'txt']:
            raise serializers.ValidationError(
                'Недопустимое расширение файла. Разрешены: jpg, jpeg, png, gif, txt'
            )
        return value


class CommentAttachmentSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения вложений к комментариям."""
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = CommentAttachment
        fields = ['id', 'image_url', 'thumbnail_url', 'uploaded_at']
        read_only_fields = fields

    @swagger_serializer_method(serializer_or_field=serializers.URLField)
    def get_image_url(self, obj):
        """Возвращает URL изображения."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url if obj.image else None

    @swagger_serializer_method(serializer_or_field=serializers.URLField)
    def get_thumbnail_url(self, obj):
        """Возвращает URL миниатюры."""
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return obj.thumbnail.url if obj.thumbnail else None


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев."""
    author = serializers.StringRelatedField(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    attachments = CommentAttachmentSerializer(many=True, read_only=True)
    replies_count = serializers.SerializerMethodField()
    post_title = serializers.CharField(source='post.title', read_only=True)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Comment
        fields = [
            'id', 'author', 'author_username', 'content', 'created_at', 'updated_at',
            'parent', 'post', 'post_title', 'is_deleted',
            'attachments', 'replies_count'
        ]
        read_only_fields = ['author', 'author_username', 'created_at', 'updated_at',
                            'replies_count', 'post_title', 'attachments']
        extra_kwargs = {
            'content': {'help_text': 'Текст комментария с базовым HTML-форматированием'},
            'parent': {'help_text': 'Родительский комментарий (если это ответ)'},
            'post': {'help_text': 'Связанный пост'},
            'is_deleted': {'help_text': 'Флаг мягкого удаления'}
        }

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
    def get_replies_count(self, obj):
        """Возвращает количество ответов на комментарий."""
        return obj.replies.filter(is_deleted=False).count()


class PostSerializer(serializers.ModelSerializer):
    """Сериализатор для постов."""
    author = serializers.StringRelatedField(read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    attachments = PostAttachmentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    recent_comments = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            'id', 'author', 'author_username', 'title', 'content',
            'is_published', 'created_at', 'updated_at', 'attachments',
            'comments_count', 'recent_comments'
        ]
        read_only_fields = ['author', 'author_username', 'created_at', 'updated_at',
                            'comments_count', 'recent_comments']
        extra_kwargs = {
            'title': {'help_text': 'Заголовок поста'},
            'content': {'help_text': 'Текст поста с базовым HTML-форматированием'},
            'is_published': {'help_text': 'Флаг публикации поста'}
        }

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
    def get_comments_count(self, obj):
        """Возвращает количество комментариев к посту."""
        return obj.comments.filter(is_deleted=False).count()

    @swagger_serializer_method(serializer_or_field=CommentSerializer(many=True))
    def get_recent_comments(self, obj):
        # Используем prefetch_related данные из recent_top_comments
        if hasattr(obj, 'recent_top_comments'):
            return CommentSerializer(obj.recent_top_comments, many=True, context=self.context).data
        return []

    def validate_title(self, value):
        """Проверяет валидность заголовка."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Заголовок не может быть пустым.')
        if len(value) > 255:
            raise serializers.ValidationError('Заголовок не должен превышать 255 символов.')
        return value

    def validate_content(self, value):
        """Проверяет валидность содержания."""
        validator = HTMLValidator()
        validator(value)
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Содержание не может быть пустым.')
        return value


class PostDetailSerializer(PostSerializer):
    """Детальный сериализатор для поста с комментариями."""
    comments = serializers.SerializerMethodField()

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + ['comments']

    @swagger_serializer_method(serializer_or_field=CommentSerializer(many=True))
    def get_comments(self, obj):
        """Возвращает все комментарии поста с древовидной структурой."""
        root_comments = obj.comments.filter(
            parent=None,
            is_deleted=False
        ).order_by('created_at')
        return CommentSerializer(root_comments, many=True, context=self.context).data


class CommentAttachmentCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания вложений к комментариям."""

    class Meta:
        model = CommentAttachment
        fields = ['image', 'comment']
        extra_kwargs = {
            'image': {
                'help_text': 'Изображение для загрузки (jpg, jpeg, png, gif), макс. 5MB'
            },
            'comment': {
                'help_text': 'ID комментария, к которому прикрепляется изображение'
            }
        }

    def validate_image(self, value):
        """Дополнительная валидация изображения."""
        max_size = 5 * 1024 * 1024  # 5 МБ
        if value.size > max_size:
            raise serializers.ValidationError(
                f'Размер изображения не должен превышать {max_size // (1024 * 1024)} МБ.'
            )

        ext = value.name.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'gif']:
            raise serializers.ValidationError(
                'Недопустимое расширение файла. Разрешены: jpg, jpeg, png, gif'
            )
        return value

    def validate(self, attrs):
        """Дополнительная валидация данных."""
        if attrs['comment'].is_deleted:
            raise serializers.ValidationError(
                'Нельзя добавлять вложения к удаленным комментариям.'
            )
        return attrs


class CommentTreeSerializer(serializers.Serializer):
    """Сериализатор для дерева комментариев."""
    comment_id = serializers.IntegerField(help_text='ID комментария')
    comment_content = serializers.CharField(help_text='Сокращенный текст комментария')
    comment_author = serializers.CharField(help_text='Автор комментария')
    ancestor_id = serializers.IntegerField(
        allow_null=True,
        help_text='ID предка в дереве (None для корневых)'
    )
    ancestor_content = serializers.CharField(
        allow_null=True,
        help_text='Сокращенный текст предка'
    )
    ancestor_author = serializers.CharField(
        allow_null=True,
        help_text='Автор предка'
    )
    depth = serializers.IntegerField(help_text='Глубина в дереве')
    created_at = serializers.DateTimeField(help_text='Дата создания')


class PostStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики постов."""
    total_posts = serializers.IntegerField(help_text='Общее количество постов')
    published_posts = serializers.IntegerField(help_text='Опубликованные посты')
    draft_posts = serializers.IntegerField(help_text='Черновики')
    total_comments = serializers.IntegerField(help_text='Всего комментариев')
    total_attachments = serializers.IntegerField(help_text='Всего вложений')
    most_commented_post = serializers.CharField(help_text='Самый комментируемый пост')
    latest_post = serializers.CharField(help_text='Последний созданный пост')


class CommentStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики комментариев."""
    total_comments = serializers.IntegerField(help_text='Всего комментариев')
    root_comments = serializers.IntegerField(help_text='Корневые комментарии')
    reply_comments = serializers.IntegerField(help_text='Ответы на комментарии')
    deleted_comments = serializers.IntegerField(help_text='Удаленные комментарии')
    comments_with_attachments = serializers.IntegerField(help_text='Комментарии с вложениями')
    max_depth = serializers.IntegerField(help_text='Максимальная глубина дерева')
    avg_depth = serializers.FloatField(help_text='Средняя глубина дерева')


class UserActivitySerializer(serializers.Serializer):
    """Сериализатор для активности пользователя."""
    user_id = serializers.IntegerField(help_text='ID пользователя')
    username = serializers.CharField(help_text='Имя пользователя')
    posts_count = serializers.IntegerField(help_text='Количество постов')
    comments_count = serializers.IntegerField(help_text='Количество комментариев')
    attachments_count = serializers.IntegerField(help_text='Количество вложений')
    last_activity = serializers.DateTimeField(help_text='Последняя активность')
    most_active_day = serializers.DateField(
        allow_null=True,
        help_text='Самый активный день'
    )