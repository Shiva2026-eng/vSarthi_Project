import { Component, inject, input } from '@angular/core';
import { AuthService } from '../../../services/auth-service';
import { Router } from '@angular/router';
@Component({
  selector: 'app-dashboard',
  imports: [],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  private authService = inject(AuthService);
  private router = inject(Router);
  name = input<string>('');
  email = input<string>('');
  id = input<string>('');
  created_at = input<string>('');
  onLogOut() {
    this.authService.removeAccessToken();
    this.router.navigate(['/']);
  }
}
