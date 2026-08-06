import { Component, inject, signal } from '@angular/core';
import { AuthService } from '../../services/auth-service';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpParams } from '@angular/common/http';
import { Router, RouterLink } from '@angular/router';
import { NotificationBanner } from '../notification-banner/notification-banner';

@Component({
  selector: 'app-login-component',
  imports: [ReactiveFormsModule, RouterLink, NotificationBanner],
  templateUrl: './login-component.html',
  styleUrl: './login-component.scss',
})
export class LoginComponent {
  private http = inject(AuthService);
  showBanner = signal<boolean>(false);
  bannerMessage = signal<string>('');
  messageType = signal<'error' | 'success'>('error');
  private router = inject(Router);
  loginForm = new FormGroup({
    email: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.email],
    }),
    password: new FormControl(),
  });
  loginUser() {
    const body = new HttpParams()
      .set('username', this.loginForm.value.email ?? '')
      .set('password', this.loginForm.value.password);
    this.http.login(body).subscribe({
      next: (response) => {
        this.http.setAccessToken(response.access_token);
        this.router.navigate(['/dashboard']);
      },
      error: (e) => {
        console.error(e.error.detail);
        this.showBanner.set(true);
        this.bannerMessage.set(e.error.detail);
        setTimeout(() => {
          this.showBanner.set(false);
        }, 2000);
      },
    });
  }
}
