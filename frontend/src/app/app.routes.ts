import { Routes } from '@angular/router';
import { SignUpComponent } from './components/sign-up-component/sign-up-component';
import { LoginComponent } from './components/login-component/login-component';
import { HeroComponent } from './components/hero-component/hero-component';
import { authGuard } from './guards/auth-guard';
import { DocumentsTable } from './components/hero-component/documents-table/documents-table';
import { CallToAction } from './components/call-to-action/call-to-action';

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
    canActivateChild: [authGuard],
    children: [
      {
        path: 'call-to-action',
        component: CallToAction,
      },
    ],
  },
];
