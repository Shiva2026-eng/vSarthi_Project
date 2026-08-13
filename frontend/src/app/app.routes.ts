import { Routes } from '@angular/router';
import { SignUpComponent } from './components/sign-up-component/sign-up-component';
import { LoginComponent } from './components/login-component/login-component';
import { HeroComponent } from './components/hero-component/hero-component';
import { authGuard } from './guards/auth-guard';

export const routes: Routes = [
  { path: '', component: LoginComponent },
  {
    path: 'signup',
    component: SignUpComponent,
  },
  {
    path: 'dashboard',
    component: HeroComponent,
    canActivate: [authGuard],
  },
];
