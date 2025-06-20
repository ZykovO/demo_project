import { Component, Input, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Comment} from '../../../../../data/interfaces/posts-interfaces';
import { PostsService} from '../../../../../data/services/posts-service';
import {AddComment} from './add-comment/add-comment';
import {ImagePreviewModal} from '../../../../../common-ui/image-preview-modal/image-preview-modal';
import {considerSettingUpAutocompletion} from '@angular/cli/src/utilities/completion';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

interface SortOption {
  key: 'author' | 'author_username' | 'created_at';
  label: string;
}

@Component({
  selector: 'app-comment-thread',
  standalone: true,
  imports: [CommonModule, FormsModule, AddComment, ImagePreviewModal],
  templateUrl: './comment-thread.html',
  styleUrl: './comment-thread.css'
})
export class CommentThread implements OnInit {
  @Input() comments: Comment[] = [];
  @Input() postId!: number;
  @Input() level: number = 0;
  @Input() parentId: number | null = null;

  private postsService = inject(PostsService);

  currentPage = 1;
  pageSize = 25;
  totalComments = 0;
  paginatedComments: Comment[] = [];
  previewImageUrl: string | null = null;
  showAddCommentForm = false;
  constructor(private sanitizer: DomSanitizer) {}
  sortOptions: SortOption[] = [
    { key: 'author', label: 'Имя пользователя' },
    { key: 'author_username', label: 'Username' },
    { key: 'created_at', label: 'Дата добавления' }
  ];

  currentSortKey: SortOption['key'] = 'created_at';
  sortDirection: 'asc' | 'desc' = 'desc';
  loadingReplies: Set<number> = new Set();
  loadedReplies: Set<number> = new Set();
  expandedComments: Set<number> = new Set();

  ngOnInit() {
    console.log(this.comments)
    this.totalComments = this.comments.length;
    this.sortAndPaginateComments();
  }

  ngOnChanges() {
    this.totalComments = this.comments.length;
    this.currentPage = 1;
    this.sortAndPaginateComments();
  }

  openImagePreview(imageUrl: string) {
    this.previewImageUrl = imageUrl;
    // Prevent the default behavior (opening in new tab)
    return false;
  }

  toggleAddCommentForm(commentId: number | null = null): void {
    this.showAddCommentForm = !this.showAddCommentForm;
    if (commentId) {
      this.parentId = commentId;
    }
  }


  // Сортировка и пагинация
  sortAndPaginateComments() {
    let sortedComments = [...this.comments];

    // Сортировка
    sortedComments.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (this.currentSortKey) {
        case 'author':
          aValue = a.author.toLowerCase();
          bValue = b.author.toLowerCase();
          break;
        case 'author_username':
          aValue = a.author_username.toLowerCase();
          bValue = b.author_username.toLowerCase();
          break;
        case 'created_at':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        default:
          return 0;
      }

      if (aValue < bValue) {
        return this.sortDirection === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return this.sortDirection === 'asc' ? 1 : -1;
      }
      return 0;
    });

    // Пагинация
    const startIndex = (this.currentPage - 1) * this.pageSize;
    const endIndex = startIndex + this.pageSize;
    this.paginatedComments = sortedComments.slice(startIndex, endIndex);
  }

  // Обработчики сортировки
  onSortChange(sortKey: SortOption['key']) {
    if (this.currentSortKey === sortKey) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.currentSortKey = sortKey;
      this.sortDirection = 'desc';
    }
    this.currentPage = 1;
    this.sortAndPaginateComments();
  }

  getSortIcon(sortKey: SortOption['key']): string {
    if (this.currentSortKey !== sortKey) return '↕️';
    return this.sortDirection === 'asc' ? '↑' : '↓';
  }

  // Пагинация
  get totalPages(): number {
    return Math.ceil(this.totalComments / this.pageSize);
  }

  get paginationInfo(): string {
    const start = (this.currentPage - 1) * this.pageSize + 1;
    const end = Math.min(this.currentPage * this.pageSize, this.totalComments);
    return `${start}-${end} из ${this.totalComments}`;
  }

  onPageChange(page: number) {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
      this.sortAndPaginateComments();
    }
  }

  getPaginationPages(): number[] {
    const pages: number[] = [];
    const maxVisiblePages = 5;
    const halfVisible = Math.floor(maxVisiblePages / 2);

    let startPage = Math.max(1, this.currentPage - halfVisible);
    let endPage = Math.min(this.totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage < maxVisiblePages - 1) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
  }

  // Работа с ответами
  async toggleReplies(comment: Comment) {
    if (this.expandedComments.has(comment.id)) {
      this.expandedComments.delete(comment.id);
      return;
    }

    this.expandedComments.add(comment.id);

    if (!this.loadedReplies.has(comment.id) && comment.replies_count > 0) {
      await this.loadReplies(comment);
    }
  }

  async loadReplies(comment: Comment) {
    if (this.loadingReplies.has(comment.id)) return;

    this.loadingReplies.add(comment.id);

    try {
      this.postsService.getCommentReplies(comment.id).subscribe({
        next: (replies) => {
          comment.replies = replies;
          comment.replies_count = replies.length; // Обновляем счетчик
          this.loadedReplies.add(comment.id);
          this.loadingReplies.delete(comment.id);
        },
        error: (error) => {
          console.error('Ошибка загрузки ответов:', error);
          this.loadingReplies.delete(comment.id);
        }
      });
    } catch (error) {
      console.error('Ошибка при загрузке ответов:', error);
      this.loadingReplies.delete(comment.id);
    }
  }

  isExpanded(commentId: number): boolean {
    return this.expandedComments.has(commentId);
  }

  isLoadingReplies(commentId: number): boolean {
    return this.loadingReplies.has(commentId);
  }
  insertTag(tag: string): void {
    const textarea = document.querySelector('.comment-textarea') as HTMLTextAreaElement;
    if (!textarea) return;

    const startPos = textarea.selectionStart;
    const endPos = textarea.selectionEnd;
    const selectedText = textarea.value.substring(startPos, endPos);

    let tagContent = '';
    let cursorPos = 0;

    switch (tag) {
      case 'a':
        tagContent = `<a href="" title="">${selectedText || 'текст ссылки'}</a>`;
        cursorPos = startPos + 9; // Позиция после href=""
        break;
      case 'i':
        tagContent = `<i>${selectedText || ''}</i>`;
        cursorPos = startPos + 3; // Позиция после <i>
        break;
      case 'strong':
        tagContent = `<strong>${selectedText || ''}</strong>`;
        cursorPos = startPos + 8; // Позиция после <strong>
        break;
      case 'code':
        tagContent = `<code>${selectedText || ''}</code>`;
        cursorPos = startPos + 6; // Позиция после <code>
        break;
    }

    const newValue =
      textarea.value.substring(0, startPos) +
      tagContent +
      textarea.value.substring(endPos);

    textarea.value = newValue;

    // Устанавливаем позицию курсора
    setTimeout(() => {
      textarea.setSelectionRange(cursorPos, cursorPos);
      textarea.focus();
    }, 0);
  }
  // Утилиты

  formatDate(date: Date | string): string {
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'short',
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

  trackByCommentId(index: number, comment: Comment): number {
    return comment.id;
  }

  formatContent(content: string): SafeHtml {
    // Сохраняем переносы строк и заменяем теги
    const formattedContent = content
      .replace(/\n/g, '<br>') // Добавляем эту строку для сохранения переносов
      .replace(/<a href="([^"]*)" title="([^"]*)">([^<]*)<\/a>/g,
        '<a href="$1" title="$2" target="_blank" rel="noopener noreferrer">$3</a>')
      .replace(/<i>([^<]*)<\/i>/g, '<em>$1</em>')
      .replace(/<strong>([^<]*)<\/strong>/g, '<strong>$1</strong>')
      .replace(/<code>([^<]*)<\/code>/g, '<code>$1</code>');

    return this.sanitizer.bypassSecurityTrustHtml(formattedContent);
  }

  onCommentAdded(): void {
    if (this.postId) {
      if (this.parentId) {
        // Если это ответ на комментарий, перезагружаем ответы для родительского комментария
        const parentComment = this.comments.find(c => c.id === this.parentId);
        if (parentComment) {
          this.loadedReplies.delete(parentComment.id);
          this.loadReplies(parentComment).then(() => {
            // После загрузки ответов, обновляем счетчик
            parentComment.replies_count = parentComment.replies?.length || 0;
            // Обновляем пагинацию
            this.sortAndPaginateComments();
          });
        }
      } else {
        // Для корневого уровня перезагружаем верхнеуровневые комментарии
        this.postsService.getPostTopLevelComments(this.postId).subscribe(comments => {
          this.comments = comments;
          this.totalComments = comments.length;
          this.sortAndPaginateComments();
          // Разворачиваем родительский комментарий, если он есть
          if (this.parentId) {
            this.expandedComments.add(this.parentId);
          }
        });
      }
    }
    this.showAddCommentForm = false;
  }
}
