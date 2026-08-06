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
  showBanner = signal<boolean>(false);
  bannerMessage = signal<string>('');
  messageType = signal<'error' | 'success'>('error');
  private router = inject(Router);
  signupForm = new FormGroup({
    name: new FormControl(),
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required]),
  });
  signupUser() {
    return this.authService.signup(this.signupForm.value).subscribe({
      next: (response) => {
        console.log(response);
        this.showBanner.set(true);
        this.bannerMessage.set('User registered successfully');
        this.messageType.set('success');
        setTimeout(() => {
          this.showBanner.set(false);
          this.router.navigate(['/']);
        }, 2000);
      },
      error: (e) => {
        console.log(e);
        this.showBanner.set(true);
        this.bannerMessage.set(e.error.detail);
        setTimeout(() => {
          this.showBanner.set(false);
        }, 2000);
      },
    });
  }
}
