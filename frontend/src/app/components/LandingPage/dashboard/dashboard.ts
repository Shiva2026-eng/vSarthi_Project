import { Component, inject, OnInit, signal } from '@angular/core';
import { AuthService } from '../../../services/auth-service';
import { Router } from '@angular/router';
@Component({
  selector: 'app-dashboard',
  imports: [],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard implements OnInit {
  private authService = inject(AuthService);
  private router = inject(Router);
  name = signal<string>('');
  email = signal<string>('');
  id = signal<string>('');
  created_at = signal<string>('');
  ngOnInit(): void {
    this.authService.getUserInfo().subscribe({
      next: (response) => {
        this.name.set(response.details.name);
        this.email.set(response.details.email);
        this.id.set(response.details.id);
        this.created_at.set(response.details.created_at);
      },
      error: (e) => {
        console.log(e);
      },
    });
  }
  onLogOut() {
    this.authService.removeAccessToken();
    this.router.navigate(['/']);
  }
}
