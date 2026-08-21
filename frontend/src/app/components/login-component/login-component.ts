import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth-service';
import { HttpParams } from '@angular/common/http';
import { environment } from '../../../environments/environment';
@Component({
  selector: 'app-login-component',
  imports: [ReactiveFormsModule, MatButtonModule, MatInputModule, MatFormFieldModule, RouterLink],
  templateUrl: './login-component.html',
  styleUrl: './login-component.scss',
})
export class LoginComponent {
  showBanner = signal<boolean>(false);
  bannerMessage = signal<string>('');
  bannerType = signal<'error' | 'success'>('success');
  private router = inject(Router);
  private authService = inject(AuthService);
  loginForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required]),
  });
  showAlertBanner(message: string, type: 'error' | 'success') {
    this.showBanner.set(true);
    this.bannerMessage.set(message);
    this.bannerType.set(type);
    setTimeout(() => {
      this.showBanner.set(false);
    }, 2000);
  }
  onLogin() {
    if (!this.loginForm.valid) {
      this.showAlertBanner('Form entries are not valid', 'error');
      return;
    }
    const body = new HttpParams()
      .set('username', this.loginForm.value.email ?? ' ')
      .set('password', this.loginForm.value.password ?? '');
    this.authService.login(body).subscribe({
      next: (response) => {
        this.router.navigate(['/dashboard']);
      },
      error: (e) => {
        this.showAlertBanner(e.error?.detail || 'Login failed', 'error');
      },
    });
  }
}
