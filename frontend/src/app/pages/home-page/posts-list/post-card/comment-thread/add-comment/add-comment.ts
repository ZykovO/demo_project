// add-comment.component.ts
import { Component, EventEmitter, Input, Output, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {PostsService} from '../../../../../../data/services/posts-service';
import {AuthService} from '../../../../../../auth/auth-service';
import {FileSizePipe} from '../../../../../../common-ui/pipes/file-size.pipe';
import {RouterLink} from '@angular/router';


@Component({
  selector: 'app-add-comment',
  standalone: true,
  imports: [CommonModule, FormsModule, FileSizePipe, RouterLink],
  templateUrl: './add-comment.html',
  styleUrls: ['./add-comment.css']
})
export class AddComment {
  @Input() postId!: number;
  @Input() parentId: number | null = null;
  @Output() commentAdded = new EventEmitter<void>();

  private postsService = inject(PostsService);
  private authService = inject(AuthService);

  content = '';
  previewMode = false;
  file: File | null = null;
  filePreview: string | null = null;
  errorMessage = '';

  get isAuthenticated(): boolean {
    return this.authService.isAuth();
  }

  onFileChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      const file = input.files[0];
      if (!file.type) {
        this.errorMessage = 'Недопустимый формат файла';
        return;
      }
      // Проверка типа файла и размера
      if (file.type.startsWith('image/')) {
        if (file.size > 5 * 1024 * 1024) { // 5MB
          this.errorMessage = 'Изображение слишком большое (макс. 5MB)';
          return;
        }
        this.processImage(file);
      } else if (file.type === 'text/plain') {
        if (file.size > 100 * 1024) { // 100KB
          this.errorMessage = 'Текстовый файл слишком большой (макс. 100KB)';
          return;
        }
        this.processTextFile(file);
      } else {
        this.errorMessage = 'Недопустимый формат файла (разрешены JPG, GIF, PNG, TXT)';
      }
    }
  }

  private processImage(file: File): void {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        // Проверка и изменение размера изображения
        if (img.width > 320 || img.height > 240) {
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');

          // Рассчитываем новые размеры с сохранением пропорций
          const ratio = Math.min(320 / img.width, 240 / img.height);
          canvas.width = img.width * ratio;
          canvas.height = img.height * ratio;

          ctx?.drawImage(img, 0, 0, canvas.width, canvas.height);

          canvas.toBlob((blob) => {
            if (blob) {
              this.file = new File([blob], file.name, { type: file.type });
              this.filePreview = canvas.toDataURL(file.type);
              this.errorMessage = '';
            }
          }, file.type);
        } else {
          this.file = file;
          this.filePreview = e.target?.result as string;
          this.errorMessage = '';
        }
      };
      img.src = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }

  private processTextFile(file: File): void {
    const reader = new FileReader();
    reader.onload = (e) => {
      this.file = file;
      this.filePreview = e.target?.result as string;
      this.errorMessage = '';
    };
    reader.readAsText(file);
  }

  removeFile(): void {
    this.file = null;
    this.filePreview = null;
  }

  togglePreview(): void {
    this.previewMode = !this.previewMode;
  }
  formatContent(content: string): string {
    // Сохраняем переносы строк и заменяем теги
    return content
      .replace(/\n/g, '<br>') // Добавляем эту строку для сохранения переносов
      .replace(/<a href="([^"]*)" title="([^"]*)">([^<]*)<\/a>/g,
        '<a href="$1" title="$2" target="_blank" rel="noopener noreferrer">$3</a>')
      .replace(/<i>([^<]*)<\/i>/g, '<em>$1</em>')
      .replace(/<strong>([^<]*)<\/strong>/g, '<strong>$1</strong>')
      .replace(/<code>([^<]*)<\/code>/g, '<code>$1</code>');
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
  submitComment(): void {
    if (!this.content.trim()) {
      this.errorMessage = 'Комментарий не может быть пустым';
      return;
    }

    const formData = new FormData();
    formData.append('content', this.content);
    formData.append('post', this.postId.toString());

    if (this.parentId) {
      formData.append('parent', this.parentId.toString());
    }

    if (this.file) {
      formData.append('attachments', this.file);
    }

    this.postsService.addComment(formData).subscribe({
      next: () => {
        this.content = '';
        this.file = null;
        this.filePreview = null;
        this.previewMode = false;
        this.errorMessage = '';
        this.commentAdded.emit(); // Это важно - эмитим событие
      },
      error: (error) => {
        this.errorMessage = error.message || 'Ошибка при добавлении комментария';
      }
    });
  }
}
