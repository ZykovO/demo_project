// notifications.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { animate, style, transition, trigger } from '@angular/animations';
import {WebsocketService} from '../../../data/services/websocket.service';
import {Notification} from '../../../data/services/websocket.service';
import {DatePipe, NgForOf, NgIf} from '@angular/common';

@Component({
  selector: 'app-notifications',
  templateUrl: './notifications.component.html',
  styleUrls: ['./notifications.component.css'],
  imports: [
    NgIf,
    NgForOf,
    DatePipe
  ],
  animations: [
    trigger('slideInOut', [
      transition(':enter', [
        style({transform: 'translateX(100%)'}),
        animate('200ms ease-in', style({transform: 'translateX(0%)'}))
      ]),
      transition(':leave', [
        animate('200ms ease-in', style({transform: 'translateX(100%)'}))
      ])
    ])
  ]
})
export class NotificationsComponent implements OnInit, OnDestroy {
  notifications: Notification[] = [];
  showPanel = false;
  unreadCount = 0;

  constructor(private websocketService: WebsocketService) {}

  ngOnInit(): void {
    this.websocketService.notifications$.subscribe(notification => {
      this.notifications.unshift(notification);
      if (!notification.read) {
        this.unreadCount++;
      }

      // Auto-remove notification after 5 seconds
      // setTimeout(() => {
      //   this.removeNotification(notification.id);
      // }, 5000);
    });
  }

  ngOnDestroy(): void {
    // Cleanup if needed
  }

  togglePanel(): void {
    this.showPanel = !this.showPanel;
    if (this.showPanel) {
      this.markAllAsRead();
      console.log(this.notifications)
    }
  }

  markAllAsRead(): void {
    this.notifications.forEach(n => n.read = true);
    this.unreadCount = 0;
  }

  removeNotification(id: string): void {
    this.notifications = this.notifications.filter(n => n.id !== id);
  }

  getNotificationIcon(type: string): string {
    switch (type) {
      case 'success': return '✓';
      case 'warning': return '⚠';
      case 'error': return '✗';
      default: return 'i';
    }
  }
}
