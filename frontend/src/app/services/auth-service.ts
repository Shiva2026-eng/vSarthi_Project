import { inject, Service } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
interface TokenResponse {
  access_token: string;
  token_type: string;
}
@Service()
export class AuthService {
  private http = inject(HttpClient);
  signup(data: any) {
    return this.http.post(`${environment.baseUrl}/auth/signup`, data);
  }
  login(data: any) {
    return this.http.post<TokenResponse>(`${environment.baseUrl}/auth/login`, data, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  }
  setAccessToken(token: string) {
    localStorage.setItem('access_token', token);
  }
  removeAccessToken() {
    localStorage.removeItem('access_token');
  }
  isLoggedIn() {
    return localStorage.getItem('access_token') != null;
  }
}
