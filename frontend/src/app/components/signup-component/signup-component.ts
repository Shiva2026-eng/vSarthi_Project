import { Component, inject, signal } from '@angular/core';
import { AuthService } from '../../services/auth-service';
import { FormGroup, FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { NotificationBanner } from '../notification-banner/notification-banner';

@Component({
  selector: 'app-signup-component',
  imports: [ReactiveFormsModule, RouterLink, NotificationBanner],
  templateUrl: './signup-component.html',
  styleUrl: './signup-component.scss',
})
export class SignupComponent {
  private authService = inject(AuthService);
  private router = inject(Router);

  showBanner = signal<boolean>(false);
  bannerMessage = signal<string>('');
  messageType = signal<'error' | 'success'>('error');
  isLoading = signal<boolean>(false);

  signupForm = new FormGroup({
    name: new FormControl('', [Validators.required]),
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required]),
  });

  signupUser() {
    if (this.signupForm.invalid) return;

    this.isLoading.set(true);
    return this.authService.signup(this.signupForm.value).subscribe({
      next: (response) => {
        console.log(response);
        this.isLoading.set(false);
        this.showBanner.set(true);
        this.bannerMessage.set('User registered successfully');
        this.messageType.set('success');
        setTimeout(() => {
          this.showBanner.set(false);
          this.router.navigate(['/']);
        }, 1500);
      },
      error: (e) => {
        console.error(e);
        this.isLoading.set(false);
        this.showBanner.set(true);
        this.messageType.set('error');
        this.bannerMessage.set(e?.error?.detail || 'Registration failed');
        setTimeout(() => {
          this.showBanner.set(false);
        }, 3000);
      },
    });
  }
}

