from rest_framework.decorators import action
from rest_framework import generics, permissions, status, parsers, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Post, PostAttachment, Comment, CommentAttachment, CommentTree
from .serializers import (
    PostSerializer, PostDetailSerializer, PostAttachmentCreateSerializer,
    PostAttachmentSerializer, CommentSerializer, CommentAttachmentSerializer,
    CommentAttachmentCreateSerializer, CommentTreeSerializer
)
from .validators import IsAuthor


class PostListView(generics.ListAPIView):
    """Список постов с фильтрацией, поиском и сортировкой."""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_published', 'author']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        # Получаем последние 3 комментария верхнего уровня (parent=None)
        recent_top_comments_prefetch = Prefetch(
            'comments',
            queryset=Comment.objects.filter(
                is_deleted=False,
                parent__isnull=True  # Только комментарии верхнего уровня
            ).select_related('author').annotate(
                replies_count=Count(
                    'replies',
                    filter=Q(replies__is_deleted=False)
                )
            ).order_by('-created_at')[:3],  # Последние 3 комментария
            to_attr='recent_top_comments'
        )

        queryset = Post.objects.select_related('author').prefetch_related(
            'attachments',
            recent_top_comments_prefetch
        ).annotate(
            comments_count=Count('comments', filter=Q(comments__is_deleted=False))
        )

        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_published=True)
        return queryset


class PostCreateView(generics.CreateAPIView):
    """Создание нового поста."""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostRetrieveView(generics.RetrieveAPIView):
    """Просмотр деталей поста."""
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        return PostDetailSerializer

    def get_queryset(self):
        # Для детального просмотра тоже используем только комментарии верхнего уровня
        recent_top_comments_prefetch = Prefetch(
            'comments',
            queryset=Comment.objects.filter(
                is_deleted=False,
                parent__isnull=True
            ).select_related('author').annotate(
                replies_count=Count(
                    'replies',
                    filter=Q(replies__is_deleted=False)
                )
            ).order_by('-created_at')[:3],
            to_attr='recent_top_comments'
        )

        return Post.objects.select_related('author').prefetch_related(
            'attachments',
            recent_top_comments_prefetch
        ).annotate(
            comments_count=Count('comments', filter=Q(comments__is_deleted=False))
        )


class PostUpdateView(generics.UpdateAPIView):
    """Обновление поста."""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthor]


class PostDestroyView(generics.DestroyAPIView):
    """Удаление поста."""
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAuthor]


class PostPublishedListView(generics.ListAPIView):
    """Список опубликованных постов."""
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        recent_top_comments_prefetch = Prefetch(
            'comments',
            queryset=Comment.objects.filter(
                is_deleted=False,
                parent__isnull=True
            ).select_related('author').annotate(
                replies_count=Count(
                    'replies',
                    filter=Q(replies__is_deleted=False)
                )
            ).order_by('-created_at')[:3],
            to_attr='recent_top_comments'
        )

        return Post.objects.filter(is_published=True).select_related('author').prefetch_related(
            'attachments',
            recent_top_comments_prefetch
        ).annotate(
            comments_count=Count('comments', filter=Q(comments__is_deleted=False))
        )


class PostMyListView(generics.ListAPIView):
    """Список постов текущего пользователя."""
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        recent_top_comments_prefetch = Prefetch(
            'comments',
            queryset=Comment.objects.filter(
                is_deleted=False,
                parent__isnull=True
            ).select_related('author').annotate(
                replies_count=Count(
                    'replies',
                    filter=Q(replies__is_deleted=False)
                )
            ).order_by('-created_at')[:3],
            to_attr='recent_top_comments'
        )

        return Post.objects.filter(author=self.request.user).select_related('author').prefetch_related(
            'attachments',
            recent_top_comments_prefetch
        ).annotate(
            comments_count=Count('comments', filter=Q(comments__is_deleted=False))
        )


class PostTogglePublishView(APIView):
    """Переключение статуса публикации поста."""
    permission_classes = [permissions.IsAuthenticated, IsAuthor]

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        self.check_object_permissions(request, post)
        post.is_published = not post.is_published
        post.save()
        serializer = PostSerializer(post)
        return Response(serializer.data)


class PostTopCommentsView(generics.ListAPIView):
    """Получение комментариев верхнего уровня для конкретного поста."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'author']
    ordering = ['-created_at']

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return Comment.objects.filter(
            post=post,
            parent__isnull=True,
            is_deleted=False
        ).select_related('author').annotate(
            replies_count=Count('replies', filter=Q(replies__is_deleted=False))
        )


class PostAttachmentListView(generics.ListAPIView):
    """Список вложений поста."""
    serializer_class = PostAttachmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['file_type', 'post']
    ordering_fields = ['uploaded_at']
    ordering = ['-uploaded_at']

    def get_queryset(self):
        return PostAttachment.objects.select_related('post', 'post__author')


class PostAttachmentCreateView(generics.CreateAPIView):
    """Создание вложения к посту."""
    serializer_class = PostAttachmentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post = serializer.validated_data['post']
        if post.author != self.request.user:
            raise PermissionDenied("Вы можете добавлять вложения только к своим постам.")
        serializer.save()


class PostAttachmentRetrieveView(generics.RetrieveAPIView):
    """Просмотр вложения поста."""
    queryset = PostAttachment.objects.all()
    serializer_class = PostAttachmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class PostAttachmentDestroyView(generics.DestroyAPIView):
    """Удаление вложения поста."""
    queryset = PostAttachment.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAuthor]

    def get_object(self):
        attachment = super().get_object()
        if attachment.post.author != self.request.user:
            raise PermissionDenied("Вы можете удалять только свои вложения.")
        return attachment


class CommentListView(generics.ListAPIView):
    """Список комментариев с фильтрацией."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['post', 'parent', 'author', 'is_deleted']
    search_fields = ['content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['created_at']

    def get_queryset(self):
        queryset = Comment.objects.select_related('author', 'post', 'parent').prefetch_related(
            'attachments',
            Prefetch(
                'replies',
                queryset=Comment.objects.filter(is_deleted=False).select_related('author')
            )
        ).annotate(
            replies_count=Count('replies', filter=Q(replies__is_deleted=False))
        )

        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_deleted=False)
        return queryset


class CommentCreateView(generics.CreateAPIView):
    """Создание комментария."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (parsers.MultiPartParser, parsers.JSONParser)

    def perform_create(self, serializer):
        # Сохраняем комментарий
        comment = serializer.save(author=self.request.user)

        # Обрабатываем вложения, если они есть
        attachments = self.request.FILES.getlist('attachments')
        print(attachments)
        for attachment in attachments:
            CommentAttachment.objects.create(
                comment=comment,
                image=attachment
            )


class CommentReplyCreateView(generics.CreateAPIView):
    """Создание ответа на комментарий."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        parent_comment = get_object_or_404(Comment, pk=kwargs['pk'])
        data = request.data.copy()
        data['parent'] = parent_comment.id
        data['post'] = parent_comment.post.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentRetrieveView(generics.RetrieveAPIView):
    """Просмотр комментария."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CommentUpdateView(generics.UpdateAPIView):
    """Обновление комментария."""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthor]


class CommentDestroyView(generics.DestroyAPIView):
    """Удаление комментария (мягкое удаление)."""
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAuthor]

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


class CommentRestoreView(APIView):
    """Восстановление удаленного комментария."""
    permission_classes = [permissions.IsAuthenticated, IsAuthor]

    def post(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        self.check_object_permissions(request, comment)
        comment.is_deleted = False
        comment.save()
        serializer = CommentSerializer(comment)
        return Response(serializer.data)


class CommentRepliesListView(generics.ListAPIView):
    """Список ответов на комментарий."""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'author']
    ordering = ['created_at']

    def get_queryset(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        return comment.replies.filter(is_deleted=False).select_related('author').annotate(
            replies_count=Count('replies', filter=Q(replies__is_deleted=False))
        )


class CommentThreadView(APIView):
    """Получение всей ветки комментариев."""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        comment = get_object_or_404(Comment, pk=pk)
        root_comment = comment
        while root_comment.parent:
            root_comment = root_comment.parent

        def get_comment_tree(parent_comment):
            replies = parent_comment.replies.filter(is_deleted=False).order_by('created_at')
            result = []
            for reply in replies:
                reply_data = CommentSerializer(reply, context={'request': request}).data
                reply_data['replies'] = get_comment_tree(reply)
                result.append(reply_data)
            return result

        root_data = CommentSerializer(root_comment, context={'request': request}).data
        root_data['replies'] = get_comment_tree(root_comment)
        return Response(root_data)


class CommentAttachmentListView(generics.ListAPIView):
    """Список вложений комментариев."""
    serializer_class = CommentAttachmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['comment']
    ordering_fields = ['uploaded_at']
    ordering = ['-uploaded_at']

    def get_queryset(self):
        return CommentAttachment.objects.select_related('comment', 'comment__author')


class CommentAttachmentCreateView(generics.CreateAPIView):
    """Создание вложения к комментарию."""
    serializer_class = CommentAttachmentCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        comment = serializer.validated_data['comment']
        if comment.author != self.request.user:
            raise PermissionDenied("Вы можете добавлять вложения только к своим комментариям.")
        if comment.is_deleted:
            raise PermissionDenied("Нельзя добавлять вложения к удаленным комментариям.")
        serializer.save()


class CommentAttachmentRetrieveView(generics.RetrieveAPIView):
    """Просмотр вложения комментария."""
    queryset = CommentAttachment.objects.all()
    serializer_class = CommentAttachmentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class CommentAttachmentDestroyView(generics.DestroyAPIView):
    """Удаление вложения комментария."""
    queryset = CommentAttachment.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsAuthor]

    def get_object(self):
        attachment = super().get_object()
        if attachment.comment.author != self.request.user:
            raise PermissionDenied("Вы можете удалять только свои вложения.")
        return attachment


class CommentTreeListView(generics.ListAPIView):
    """Список связей в дереве комментариев."""
    serializer_class = CommentTreeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['comment', 'ancestor', 'depth']
    ordering_fields = ['depth']
    ordering = ['depth']

    def get_queryset(self):
        return CommentTree.objects.select_related('comment', 'ancestor')


class CommentAncestorsListView(generics.ListAPIView):
    """Список предков комментария."""
    serializer_class = CommentTreeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        return CommentTree.objects.filter(comment=comment).exclude(depth=0).order_by('depth')


class CommentDescendantsListView(generics.ListAPIView):
    """Список потомков комментария."""
    serializer_class = CommentTreeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        comment = get_object_or_404(Comment, pk=self.kwargs['pk'])
        return CommentTree.objects.filter(ancestor=comment).exclude(depth=0).order_by('depth')




class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (parsers.MultiPartParser, parsers.JSONParser)

    def perform_create(self, serializer):
        # Сохраняем комментарий
        comment = serializer.save(author=self.request.user)

        # Обрабатываем вложения, если они есть
        attachments = self.request.FILES.getlist('attachments')
        for attachment in attachments:
            CommentAttachment.objects.create(
                comment=comment,
                image=attachment
            )

    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """Создание ответа на комментарий."""
        parent_comment = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(
            author=request.user,
            parent=parent_comment,
            post=parent_comment.post
        )
        return Response(serializer.data, status=201)