import { inject, Service } from '@angular/core';
import { HttpClient } from '@angular/common/http';
interface TokenResponse {
  access_token: string;
  token_type: string;
}
export interface ConnectedAccounts {
  telegram: boolean;
  outlook: boolean;
}

export interface UserDetails {
  id: string;
  name: string;
  email: string;
  created_at: string;
  connected_accounts: ConnectedAccounts;
}

export interface UserProfileResponse {
  success: boolean;
  details: UserDetails;
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
    return this.http.get<UserProfileResponse>('http://127.0.0.1:8000/user/my_profile');
  }
}
