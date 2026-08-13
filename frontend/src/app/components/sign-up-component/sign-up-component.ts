import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth-service';
@Component({
  selector: 'app-sign-up-component',
  imports: [ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, RouterLink],
  templateUrl: './sign-up-component.html',
  styleUrl: './sign-up-component.scss',
})
export class SignUpComponent {
  private authService = inject(AuthService);
  private router = inject(Router);
  signupForm = new FormGroup({
    name: new FormControl('', [Validators.required]),
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required]),
  });
  onSignup() {
    if (!this.signupForm.valid) {
      alert('The form is not valid');
      return;
    }
    this.authService.signup(this.signupForm.value).subscribe({
      next: (response) => {
        console.log(response);
        setTimeout(() => {
          this.router.navigate(['/']);
        }, 2000);
      },
      error: (e) => {
        console.log(e.detail);
      },
    });
  }
}
