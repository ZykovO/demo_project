// posts-service.ts
import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { Post, Comment } from '../interfaces/posts-interfaces';
import {environment} from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PostsService {
  private readonly http = inject(HttpClient);
  private readonly baseApiUrl = environment.apiUrl;

  constructor() {}

  /**
   * Получить все посты
   */
  getAllPosts(): Observable<Post[]> {
    return this.http.get<Post[]>(`${this.baseApiUrl}posts/`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Получить комментарии верхнего уровня для конкретного поста
   */
  getPostTopLevelComments(postId: number): Observable<Comment[]> {
    if (!postId || postId <= 0) {
      return throwError(() => new Error('Некорректный ID поста'));
    }

    return this.http.get<Comment[]>(`${this.baseApiUrl}posts/${postId}/top-comments/`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Получить список ответов на комментарий с пагинацией
   */
  getCommentReplies(commentId: number, page: number = 1, pageSize: number = 25): Observable<Comment[]> {
    if (!commentId || commentId <= 0) {
      return throwError(() => new Error('Некорректный ID комментария'));
    }

    const params = {
      page: page.toString(),
      page_size: pageSize.toString()
    };

    return this.http.get<Comment[]>(`${this.baseApiUrl}comments/${commentId}/replies/`, { params })
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Получить конкретный пост по ID
   */
  getPost(postId: number): Observable<Post> {
    if (!postId || postId <= 0) {
      return throwError(() => new Error('Некорректный ID поста'));
    }

    return this.http.get<Post>(`${this.baseApiUrl}posts/${postId}/`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Получить конкретный комментарий по ID
   */
  getComment(commentId: number): Observable<Comment> {
    if (!commentId || commentId <= 0) {
      return throwError(() => new Error('Некорректный ID комментария'));
    }

    return this.http.get<Comment>(`${this.baseApiUrl}comments/${commentId}/`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Добавить новый комментарий
   */
  addComment(formData: FormData): Observable<Comment> {
    return this.http.post<Comment>(`${this.baseApiUrl}comments/`, formData, {
      headers: {
        // Angular обычно автоматически добавляет нужные заголовки для FormData,
        // но если есть проблемы, можно явно указать:
        //  'Content-Type': 'multipart/form-data'
      }
    }).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Проверить валидность HTML тегов
   */
  validateTags(content: string): Observable<{ valid: boolean, message?: string }> {
    return this.http.post<{ valid: boolean, message?: string }>(
      `${this.baseApiUrl}comments/validate-tags/`,
      { content }
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Обработка ошибок HTTP запросов
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'Произошла неизвестная ошибка';

    if (error.error instanceof ErrorEvent) {
      // Ошибка на стороне клиента
      errorMessage = `Ошибка клиента: ${error.error.message}`;
    } else {
      // Ошибка на стороне сервера
      switch (error.status) {
        case 0:
          errorMessage = 'Не удается подключиться к серверу';
          break;
        case 404:
          errorMessage = 'Запрашиваемый ресурс не найден';
          break;
        case 500:
          errorMessage = 'Внутренняя ошибка сервера';
          break;
        case 503:
          errorMessage = 'Сервер временно недоступен';
          break;
        default:
          errorMessage = `Ошибка сервера: ${error.status} - ${error.message}`;
      }
    }

    console.error('PostsService Error:', errorMessage, error);
    return throwError(() => new Error(errorMessage));
  }

}
