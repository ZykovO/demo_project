import { Component, Input, OnInit, inject } from '@angular/core';
import {CommonModule, NgOptimizedImage} from '@angular/common';
import {CommentThread} from './comment-thread/comment-thread';
import {Post} from '../../../../data/interfaces/posts-interfaces';
import {PostsService} from '../../../../data/services/posts-service';
import {AddComment} from './comment-thread/add-comment/add-comment';
import {ImagePreviewModal} from '../../../../common-ui/image-preview-modal/image-preview-modal';


@Component({
  selector: 'app-post-card',
  standalone: true,
  imports: [CommonModule, CommentThread, AddComment, ImagePreviewModal, NgOptimizedImage],
  templateUrl: './post-card.html',
  styleUrl: './post-card.css'
})
export class PostCard implements OnInit {
  @Input() post!: Post;


  private postsService = inject(PostsService);

  topLevelComments = [];
  isCommentsLoaded = false;
  isLoadingComments = false;
  errorMessage = '';
  showCommentForm = false;
  previewImageUrl: string | null = null;

  ngOnInit() {
    console.log(this.post)
    if (this.post?.id) {
      this.loadTopLevelComments();
    }
  }

  onCommentAdded(): void {
    this.loadTopLevelComments();
    this.showCommentForm = false;

    // Обновляем счетчик комментариев
    if (this.post) {
      this.post.comments_count += 1;
    }
  }

  openImagePreview(event: MouseEvent, imageUrl: string): void {
    event.preventDefault();
    this.previewImageUrl = imageUrl;
  }

  loadTopLevelComments() {
    this.isLoadingComments = true;
    this.errorMessage = '';

    this.postsService.getPostTopLevelComments(this.post.id).subscribe({
      next: (comments) => {
        // @ts-ignore
        this.topLevelComments = comments;
        this.isCommentsLoaded = true;
        this.isLoadingComments = false;
      },
      error: (error) => {
        this.errorMessage = error.message || 'Ошибка при загрузке комментариев';
        this.isLoadingComments = false;
        console.error('Ошибка загрузки комментариев:', error);
      }
    });
  }

  formatDate(date: Date | string): string {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  getFileIcon(fileType: string | undefined): string {
    if (!fileType) return '📎'; // Default icon if fileType is undefined
    const type = fileType.toLowerCase();
    if (type.startsWith('image')) return '🖼️';
    if (type.startsWith('video')) return '🎥';
    if (type.startsWith('audio')) return '🎵';
    if (type.includes('pdf')) return '📄';
    return '📎';
  }
}
