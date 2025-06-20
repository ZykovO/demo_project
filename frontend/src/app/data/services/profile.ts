import {inject, Injectable, signal} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {UserResponse} from '../../auth/auth-interface';
import {tap} from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProfileService {
  http = inject(HttpClient)
  baseApiUrl = 'http://127.0.0.1:8000/api/';
  me=signal<UserResponse|null>(null)
  constructor() { }

  getProfile() {
    return this.http.get<UserResponse>(`${this.baseApiUrl}auth/profile/`)
      .pipe(
        tap(profile => {
          this.me.set(profile);
        })
      )
  }
}
