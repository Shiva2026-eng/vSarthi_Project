import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from './auth-service';
import { environment } from '../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [AuthService, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should send signup request', () => {
    const signupData = { name: 'Test', email: 'test@example.com', password: 'secretpassword' };

    service.signup(signupData).subscribe((res) => {
      expect(res).toEqual({ success: true });
    });

    const req = httpMock.expectOne(`${environment.baseUrl}/auth/signup`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(signupData);
    req.flush({ success: true });
  });

  it('should send login request with form headers', () => {
    const loginData = 'username=test%40example.com&password=secretpassword';

    service.login(loginData).subscribe((res) => {
      expect(res).toBeDefined();
    });

    const req = httpMock.expectOne(`${environment.baseUrl}/auth/login`);
    expect(req.request.method).toBe('POST');
    expect(req.request.headers.get('Content-Type')).toBe('application/x-www-form-urlencoded');
    req.flush({ success: true });
  });

  it('should send logout request', () => {
    service.logout().subscribe((res) => {
      expect(res).toEqual({ success: true });
    });

    const req = httpMock.expectOne(`${environment.baseUrl}/auth/logout`);
    expect(req.request.method).toBe('POST');
    req.flush({ success: true });
  });

  it('should return true on checkAuth when user profile returns successfully', async () => {
    const checkPromise = service.checkAuth();

    const req = httpMock.expectOne(`${environment.baseUrl}/user/my_profile`);
    expect(req.request.method).toBe('GET');
    req.flush({
      success: true,
      details: { id: '1', email: 'test@example.com', name: 'Test', username: 'test' },
    });

    const isAuthenticated = await checkPromise;
    expect(isAuthenticated).toBe(true);
  });

  it('should return false on checkAuth when user profile fails', async () => {
    const checkPromise = service.checkAuth();

    const req = httpMock.expectOne(`${environment.baseUrl}/user/my_profile`);
    expect(req.request.method).toBe('GET');
    req.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });

    const isAuthenticated = await checkPromise;
    expect(isAuthenticated).toBe(false);
  });
});
