import {inject, Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {catchError, tap, throwError} from 'rxjs';
import {RefreshTokenResponse, TokenResponse} from './auth-interface';
import {CookieService} from 'ngx-cookie-service';
import {Router} from '@angular/router';
import { environment} from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  http=inject(HttpClient)
  cookieService=inject(CookieService);
  router=inject(Router)
  baseApiUrl = environment.apiUrl;
  token: string|null = null;
  refresh: string|null = null;

  isAuth() {
    if (!this.token) {
      this.token=this.cookieService.get('token');
      this.refresh=this.cookieService.get('refresh');
    }
    return !!this.token;
  }

  login(payload: {email: string, password: string}) {
    return this.http.post<TokenResponse>(`${this.baseApiUrl}auth/login/`, payload).pipe(
      tap(res => {
          this.token = res.access
          this.refresh = res.refresh

          this.cookieService.set('token', this.token);
          this.cookieService.set('refresh', this.refresh);
        }

      )
    )
  }
  register(payload: {email: string, password: string}) {
    return this.http.post<TokenResponse>(`${this.baseApiUrl}auth/register/`, payload)
  }

  logout() {
    this.cookieService.deleteAll()
    this.token=null
    this.refresh=null
    this.router.navigate(['/login'])
  }

  refreshToken() {
    return this.http.post<RefreshTokenResponse>(`${this.baseApiUrl}auth/refresh/`, {
      refresh: this.refresh
    }).pipe(
      catchError(err => {
        this.logout()
        return throwError(err)
      }),
      tap(res => {
        this.token = res.access
        this.cookieService.set('token', res.access);
      })

    )
  }
}
