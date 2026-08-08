import { inject, Service } from '@angular/core';
import { HttpClient } from '@angular/common/http';
interface TokenResponse {
  access_token: string;
  token_type: string;
}
interface UserResponse {
  success: boolean;
  details: {
    id: string;
    name: string;
    email: string;
    created_at: string;
  };
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
    if (token) {
      localStorage.setItem('access_token', token);
    }
  }

  getAccessToken(): string {
    const token = localStorage.getItem('access_token');
    return token && token.trim() !== '' ? token : '';
  }

  removeAccessToken() {
    localStorage.removeItem('access_token');
  }

  isLoggedIn(): boolean {
    return this.getAccessToken().length > 0;
  }

  getUserInfo() {
    const token = this.getAccessToken();
    return this.http.get<UserResponse>('http://127.0.0.1:8000/user/my_profile', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  }
}

