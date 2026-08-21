import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from './auth-service';
import { environment } from '../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.clear();
    }
    TestBed.configureTestingModule({
      providers: [
        AuthService,
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    if (httpMock) {
      httpMock.verify();
    }
    if (typeof window !== 'undefined' && window.localStorage) {
      window.localStorage.clear();
    }
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should handle login and update loggedIn state', () => {
    const mockData = { username: 'test@example.com', password: 'password' };
    const mockResponse = { access_token: 'dummy_token', token_type: 'Bearer' };

    service.login(mockData).subscribe((res) => {
      expect(res).toEqual(mockResponse);
      expect(service.isLoggedIn()).toBe(true);
    });

    const req = httpMock.expectOne(`${environment.baseUrl}/auth/login`);
    expect(req.request.method).toBe('POST');
    req.flush(mockResponse);
  });

  it('should handle logout and clear state', () => {
    service.setLoggedIn(true);
    expect(service.isLoggedIn()).toBe(true);

    service.logout().subscribe(() => {
      expect(service.isLoggedIn()).toBe(false);
    });

    const req = httpMock.expectOne(`${environment.baseUrl}/auth/logout`);
    expect(req.request.method).toBe('POST');
    req.flush({ success: true, message: 'Successfully logged out' });
  });
});

