import {Component, inject} from '@angular/core';
import {ProfileService} from '../../data/services/profile';
import {firstValueFrom} from 'rxjs';
import {JsonPipe} from '@angular/common';
import {AuthService} from '../../auth/auth-service';
import {Router} from '@angular/router';
import {RouterLink, RouterLinkActive} from '@angular/router';

interface NavItem {
  path: string;
  title: string;
  requiresAuth: boolean;
  exact?: boolean; // Добавляем необязательное поле
}

@Component({
  selector: 'app-sidebar',
  imports: [
    RouterLink,
    RouterLinkActive
  ],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.css'
})
export class Sidebar {
  authService = inject(AuthService);
  profileService = inject(ProfileService);
  router = inject(Router);
  me = this.profileService.me;

  // Список навигационных элементов
  navItems: NavItem[] = [
    { path: '/', title: 'Головна', requiresAuth: false, exact: true },
    // { path: '/posts', title: 'Мої записи', requiresAuth: true },
    // { path: '/profile', title: 'Профіль', requiresAuth: true }
  ];

  ngOnInit() {
    if (this.authService.isAuth()) {
      firstValueFrom(this.profileService.getProfile());
    }
  }

  navigateToProfile() {
    this.router.navigate(['/profile']);
  }

  navigateToLogin() {
    this.authService.logout();
  }

  // Проверка, должен ли элемент отображаться
  shouldShowItem(item: NavItem): boolean {
    return !item.requiresAuth || this.authService.isAuth();
  }
}
