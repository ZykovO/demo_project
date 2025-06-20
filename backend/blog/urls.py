from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    PostListView, PostCreateView, PostRetrieveView, PostUpdateView, PostDestroyView,
    PostPublishedListView, PostMyListView, PostTogglePublishView, PostTopCommentsView,
    PostAttachmentListView, PostAttachmentCreateView, PostAttachmentRetrieveView, PostAttachmentDestroyView,
    CommentListView, CommentCreateView, CommentReplyCreateView, CommentRetrieveView,
    CommentUpdateView, CommentDestroyView, CommentRestoreView, CommentRepliesListView,
    CommentThreadView, CommentAttachmentListView, CommentAttachmentCreateView,
    CommentAttachmentRetrieveView, CommentAttachmentDestroyView,
    CommentTreeListView, CommentAncestorsListView, CommentDescendantsListView, CommentViewSet
)
router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')
urlpatterns = [
    # Посты
    path('posts/', PostListView.as_view(), name='post-list'),
    path('posts/create/', PostCreateView.as_view(), name='post-create'),
    path('posts/<int:pk>/', PostRetrieveView.as_view(), name='post-detail'),
    path('posts/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('posts/<int:pk>/delete/', PostDestroyView.as_view(), name='post-delete'),
    path('posts/published/', PostPublishedListView.as_view(), name='post-published'),
    path('posts/my/', PostMyListView.as_view(), name='post-my'),
    path('posts/<int:pk>/toggle-publish/', PostTogglePublishView.as_view(), name='post-toggle-publish'),
    path('posts/<int:pk>/top-comments/', PostTopCommentsView.as_view(), name='post-top-comments'),

    # Вложения постов
    path('post-attachments/', PostAttachmentListView.as_view(), name='post-attachment-list'),
    path('post-attachments/create/', PostAttachmentCreateView.as_view(), name='post-attachment-create'),
    path('post-attachments/<int:pk>/', PostAttachmentRetrieveView.as_view(), name='post-attachment-detail'),
    path('post-attachments/<int:pk>/delete/', PostAttachmentDestroyView.as_view(), name='post-attachment-delete'),

    # Комментарии
    # path('comments/', CommentListView.as_view(), name='comment-list'),
    # path('comments/create/', CommentCreateView.as_view(), name='comment-create'),
    # path('comments/<int:pk>/reply/', CommentReplyCreateView.as_view(), name='comment-reply'),
    # path('comments/<int:pk>/', CommentRetrieveView.as_view(), name='comment-detail'),
    # path('comments/<int:pk>/update/', CommentUpdateView.as_view(), name='comment-update'),
    # path('comments/<int:pk>/delete/', CommentDestroyView.as_view(), name='comment-delete'),
    # path('comments/<int:pk>/restore/', CommentRestoreView.as_view(), name='comment-restore'),
    path('comments/<int:pk>/replies/', CommentRepliesListView.as_view(), name='comment-replies'),
    path('comments/<int:pk>/thread/', CommentThreadView.as_view(), name='comment-thread'),
    #
    # # Вложения комментариев
    # path('comment-attachments/', CommentAttachmentListView.as_view(), name='comment-attachment-list'),
    # path('comment-attachments/create/', CommentAttachmentCreateView.as_view(), name='comment-attachment-create'),
    # path('comment-attachments/<int:pk>/', CommentAttachmentRetrieveView.as_view(), name='comment-attachment-detail'),
    # path('comment-attachments/<int:pk>/delete/', CommentAttachmentDestroyView.as_view(),
    #      name='comment-attachment-delete'),
    #
    # # Дерево комментариев
    # path('comment-tree/', CommentTreeListView.as_view(), name='comment-tree-list'),
    # path('comment-tree/<int:pk>/ancestors/', CommentAncestorsListView.as_view(), name='comment-ancestors'),
    # path('comment-tree/<int:pk>/descendants/', CommentDescendantsListView.as_view(), name='comment-descendants'),


] + router.urls

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/notifications/', consumers.NotificationConsumer.as_asgi()),
]