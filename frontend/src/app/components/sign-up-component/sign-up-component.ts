import { Component, inject, signal } from '@angular/core';
import { ReactiveFormsModule, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth-service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-sign-up-component',
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    RouterLink,
    CommonModule,
  ],
  templateUrl: './sign-up-component.html',
  styleUrl: './sign-up-component.scss',
})
export class SignUpComponent {
  private authService = inject(AuthService);
  private router = inject(Router);
  showBanner = signal<boolean>(false);
  bannerMessage = signal<string>('');
  bannerType = signal<'error' | 'success'>('success');
  signupForm = new FormGroup({
    name: new FormControl('', [Validators.required]),
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
  onSignup() {
    if (!this.signupForm.valid) {
      this.showAlertBanner('Form entries are not valid', 'error');
      return;
    }
    this.authService.signup(this.signupForm.value).subscribe({
      next: (response) => {
        console.log(response);
        this.showAlertBanner('User registered Successfully', 'success');
        setTimeout(() => {
          this.router.navigate(['/']);
        }, 2000);
      },
      error: (e) => {
        this.showAlertBanner(e.error.detail, 'error');
      },
    });
  }
}
