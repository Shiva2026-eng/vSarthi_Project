import { CanActivateFn } from '@angular/router';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth-service';
import { inject } from '@angular/core';
export const authGuard: CanActivateFn = (route, state) => {
  const auth_service = inject(AuthService);
  const router = inject(Router);
  return auth_service.getAccessToken() ? true : router.createUrlTree(['/']);
};
