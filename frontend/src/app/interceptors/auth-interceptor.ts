import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth-service';
import { catchError, throwError } from 'rxjs';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  const isAuthRoute = req.url.includes('/auth/login') || req.url.includes('/auth/signup');
  const token = authService.getAccessToken();

  if (!isAuthRoute && (!token || token.trim() === '')) {
    authService.removeAccessToken();
    router.navigate(['/']);
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 || error.status === 403) {
        console.warn('Authentication token expired or invalid. Redirecting to login.');
        authService.removeAccessToken();
        router.navigate(['/']);
      }
      return throwError(() => error);
    })
  );
};
