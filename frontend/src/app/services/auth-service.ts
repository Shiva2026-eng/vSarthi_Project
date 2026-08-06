import { inject, Service } from '@angular/core';
import { HttpClient } from '@angular/common/http';
interface TokenResponse {
  access_token: string;
  token_type: string;
}
@Service()
export class AuthService {
  private http = inject(HttpClient);
  login(data: any) {
    return this.http.post<TokenResponse>('http://127.0.0.1:8000/auth/login', data, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
  }
  signup(data: any) {
    return this.http.post('http://127.0.0.1:8000/auth/signup', data);
  }
  setAccessToken(token: string) {
    localStorage.setItem('access_token', token);
  }
  getAccessToken(): string {
    return localStorage.getItem('access_token') ?? '';
  }
  removeAccessToken() {
    localStorage.setItem('access_token', '');
  }
}
