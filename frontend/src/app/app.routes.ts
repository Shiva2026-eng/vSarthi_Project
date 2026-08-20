import { Routes } from '@angular/router';
import { authGuard } from './guards/auth-guard';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./components/login-component/login-component').then(
        (m) => m.LoginComponent
      ),
  },
  {
    path: 'signup',
    loadComponent: () =>
      import('./components/sign-up-component/sign-up-component').then(
        (m) => m.SignUpComponent
      ),
  },
  {
    path: 'dashboard',
    loadComponent: () =>
      import('./components/hero-component/hero-component').then(
        (m) => m.HeroComponent
      ),
    canActivate: [authGuard],
    canActivateChild: [authGuard],
    children: [
      {
        path: 'call-to-action',
        loadComponent: () =>
          import('./components/call-to-action/call-to-action').then(
            (m) => m.CallToAction
          ),
      },
    ],
  },
];
