import { TestBed } from '@angular/core/testing';
import {
  HttpClient,
  provideHttpClient,
  withInterceptors,
} from '@angular/common/http';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { apiKeyInterceptor } from './api-key.interceptor';

describe('apiKeyInterceptor', () => {
  let http: HttpClient;
  let controller: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([apiKeyInterceptor])),
        provideHttpClientTesting(),
      ],
    });
    http = TestBed.inject(HttpClient);
    controller = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    controller.verify();
    localStorage.removeItem('notifier_api_key');
  });

  it('adds Authorization header when API key exists in localStorage', () => {
    localStorage.setItem('notifier_api_key', 'ntf_testkey123');

    http.get('/test').subscribe();

    const req = controller.expectOne('/test');
    expect(req.request.headers.get('Authorization')).toBe('Api-Key ntf_testkey123');
    req.flush({});
  });

  it('does not add Authorization header when API key is absent', () => {
    localStorage.removeItem('notifier_api_key');

    http.get('/test').subscribe();

    const req = controller.expectOne('/test');
    expect(req.request.headers.has('Authorization')).toBeFalse();
    req.flush({});
  });
});
