import { inject, Injectable, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { tap, catchError } from 'rxjs/operators';
import { of } from 'rxjs';

interface TokenResponse {
  access_token: string;
  token_type: string;
}

function getStoredAuthState(): boolean {
  if (typeof window !== 'undefined' && typeof window.localStorage !== 'undefined' && window.localStorage) {
    return window.localStorage.getItem('is_logged_in') === 'true';
  }
  return false;
}

function setStoredAuthState(status: boolean): void {
  if (typeof window !== 'undefined' && typeof window.localStorage !== 'undefined' && window.localStorage) {
    if (status) {
      window.localStorage.setItem('is_logged_in', 'true');
    } else {
      window.localStorage.removeItem('is_logged_in');
      window.localStorage.removeItem('access_token');
    }
  }
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private http = inject(HttpClient);
  private loggedIn = signal<boolean>(getStoredAuthState());

  signup(data: any) {
    return this.http.post(`${environment.baseUrl}/auth/signup`, data);
  }

  login(data: any) {
    return this.http
      .post<TokenResponse>(`${environment.baseUrl}/auth/login`, data, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      .pipe(
        tap(() => {
          this.setLoggedIn(true);
        })
      );
  }

  logout() {
    return this.http.post(`${environment.baseUrl}/auth/logout`, {}).pipe(
      tap(() => {
        this.setLoggedIn(false);
      }),
      catchError(() => {
        this.setLoggedIn(false);
        return of(null);
      })
    );
  }

  setLoggedIn(status: boolean) {
    this.loggedIn.set(status);
    setStoredAuthState(status);
  }

  isLoggedIn() {
    return this.loggedIn() || getStoredAuthState();
  }
}
