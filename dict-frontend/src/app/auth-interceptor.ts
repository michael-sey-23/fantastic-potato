import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from './auth.service';
import { tap } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = localStorage.getItem('auth_token');

  // 1. Proactive check: if token is expired, logout immediately
  if (token && authService.isTokenExpired()) {
    authService.logout();
    return next(req); // Or skip the request
  }

  // ONLY add the token if we aren't already trying to log in!
  if (token && !req.url.includes('/api/auth/login')) {
    const cloned = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    
    return next(cloned).pipe(
      tap({
        error: (error) => {
          if (error instanceof HttpErrorResponse && error.status === 401) {
             // 2. Reactive check: if server says 401, logout
             authService.logout();
          }
        }
      })
    );
  }

  return next(req);
};

