// websocket.service.ts
import {inject, Injectable, OnDestroy} from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { catchError, retry, tap } from 'rxjs/operators';
import { Observable, EMPTY, Subject } from 'rxjs';
import { environment } from '../../environments/environment';
import {AuthService} from '../../auth/auth-service';

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class WebsocketService implements OnDestroy {
  private socket$!: WebSocketSubject<any>; // Add definite assignment assertion
  private notificationsSubject = new Subject<Notification>();
  public notifications$ = this.notificationsSubject.asObservable();
  private authService = inject(AuthService);

  constructor() {
    if (this.authService.isAuth()){
      this.connect();
    }

  }

  private getWebSocketConfig() {
    const token = this.authService.token;
    const url = `${environment.wsUrl}?token=${token}`;

    return {
      url,
      openObserver: {
        next: () => console.log('WebSocket connection established')
      },
      closeObserver: {
        next: () => {
          console.log('WebSocket connection closed');
          setTimeout(() => this.connect(), 5000);
        }
      }
    };
  }


  private connect(): void {
    if (!this.socket$ || this.socket$.closed) {
      this.socket$ = webSocket(this.getWebSocketConfig());

      this.socket$.pipe(
        tap((message) => this.handleIncomingMessage(message)),
        catchError(error => {
          console.error('WebSocket error:', error);
          return EMPTY;
        })
      ).subscribe();
    }
  }

  private handleIncomingMessage(message: any): void {
    console.log('Incoming message:', message);

    if (message.type === 'notification' && message.notification) {
      const incoming = message.notification;

      const notification: Notification = {
        id: incoming.id || Date.now().toString(),
        type: incoming.type || 'info',
        title: incoming.title || 'Уведомление',
        message: incoming.message || '',
        timestamp: new Date(incoming.timestamp), // корректная дата
        read: incoming.read ?? false
      };

      this.notificationsSubject.next(notification);
    }
  }


  public sendMessage(message: any): void {
    if (this.socket$ && !this.socket$.closed) {
      this.socket$.next(message);
    }
  }

  ngOnDestroy(): void {
    if (this.socket$) {
      this.socket$.complete();
    }
  }
}
