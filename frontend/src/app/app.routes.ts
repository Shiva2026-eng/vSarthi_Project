import { Routes } from '@angular/router';
import { LoginComponent } from './components/login-component/login-component';
import { SignupComponent } from './components/signup-component/signup-component';
import { LandingPage } from './pages/landing-page/landing-page';

export const routes: Routes = [
  {
    path: '',
    component: LoginComponent,
  },
  {
    path: 'signup',
    component: SignupComponent,
  },
  {
    path: 'dashboard',
    component: LandingPage,
  },
];
