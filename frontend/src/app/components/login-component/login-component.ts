import { Component } from '@angular/core';
import { ReactiveFormsModule, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink } from '@angular/router';
@Component({
  selector: 'app-login-component',
  imports: [ReactiveFormsModule, MatButtonModule, MatInputModule, MatFormFieldModule, RouterLink],
  templateUrl: './login-component.html',
  styleUrl: './login-component.scss',
})
export class LoginComponent {
  loginForm = new FormGroup({
    email: new FormControl('', [Validators.required]),
    password: new FormControl('', [Validators.required]),
  });
  onLogin() {
    if (this.loginForm.valid) console.log(this.loginForm.value);
    else console.log('Invalid username or password');
  }
}
