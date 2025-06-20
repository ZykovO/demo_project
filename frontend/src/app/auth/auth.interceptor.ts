import {HttpHandlerFn, HttpInterceptorFn, HttpRequest} from '@angular/common/http';
import {inject} from '@angular/core';
import {AuthService} from './auth-service';
import {BehaviorSubject, catchError, filter, switchMap, tap, throwError} from 'rxjs';

let isRefreshing$ = new BehaviorSubject<boolean>(false);

export const authTokenInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService)
  authService.isAuth()
  const token = authService.token
  if (!token) return next(req);

  if (isRefreshing$.value) {
    return refreshAndProceed(authService, req, next)
  }

  return next(addtoken(req, token))
    .pipe(
      catchError(err => {
        if (err.status === 401) {
          return refreshAndProceed(authService, req, next)
        }
        return throwError(err)
      })
    )
}


const refreshAndProceed = (authService: AuthService, req: HttpRequest<any>, next: HttpHandlerFn) => {
  if (!isRefreshing$.value) {
    isRefreshing$.next(true);
    return authService.refreshToken()
      .pipe(
        switchMap(res => {
          return next(addtoken(req, res.access))
            .pipe(
              tap(() => {
                isRefreshing$.next(false)
              })
            )
        })
      )
  }

  if (req.url.includes('refresh')) return next(addtoken(req, authService.token!))

  return isRefreshing$.pipe(
    filter(isRefreshing => !isRefreshing),
    switchMap(res => {
      return next(addtoken(req, authService.token!))
    })
  )

}


const addtoken = (req: HttpRequest<any>, token: string) => {
  return req.clone(
    {
      setHeaders: {Authorization: `Bearer ${token}`}
    },
  )
}
