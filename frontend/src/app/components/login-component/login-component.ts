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
  private router = inject(Router);

  showBanner = signal<boolean>(false);
  bannerMessage = signal<string>('');
  messageType = signal<'error' | 'success'>('error');
  isLoading = signal<boolean>(false);

  loginForm = new FormGroup({
    email: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required, Validators.email],
    }),
    password: new FormControl('', {
      nonNullable: true,
      validators: [Validators.required],
    }),
  });

  loginUser() {
    if (this.loginForm.invalid) return;

    this.isLoading.set(true);
    const body = new HttpParams()
      .set('username', this.loginForm.value.email ?? '')
      .set('password', this.loginForm.value.password ?? '');

    this.http.login(body).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.http.setAccessToken(response.access_token);
        this.router.navigate(['/dashboard']);
      },
      error: (e) => {
        this.isLoading.set(false);
        console.error(e?.error?.detail);
        this.showBanner.set(true);
        this.messageType.set('error');
        this.bannerMessage.set(e?.error?.detail || 'Invalid email or password');
        setTimeout(() => {
          this.showBanner.set(false);
        }, 3000);
      },
    });
  }
}

