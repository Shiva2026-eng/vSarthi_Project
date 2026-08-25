import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { firstValueFrom } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private baseUrl = environment.baseUrl;

  signup(data: any) {
    return this.http.post(`${this.baseUrl}/auth/signup`, data);
  }

  login(data: any) {
    return this.http.post(`${this.baseUrl}/auth/login`, data, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  }

  logout() {
    return this.http.post(`${this.baseUrl}/auth/logout`, {});
  }

  async checkAuth(): Promise<boolean> {
    try {
      await firstValueFrom(this.http.get(`${this.baseUrl}/user/my_profile`));
      return true;
    } catch {
      return false;
    }
  }
}
