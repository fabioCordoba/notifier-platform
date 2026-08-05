import { TestBed } from '@angular/core/testing';
import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { NotificationService } from './notification.service';
import { environment } from '../../../environments/environment';
import { SendNotificationPayload } from '../models/notification.model';

const BASE = `${environment.apiUrl}/api/v1/notifications`;

describe('NotificationService', () => {
  let service: NotificationService;
  let controller: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(NotificationService);
    controller = TestBed.inject(HttpTestingController);
  });

  afterEach(() => controller.verify());

  it('list() calls GET /api/v1/notifications/', () => {
    service.list().subscribe();
    const req = controller.expectOne(`${BASE}/`);
    expect(req.request.method).toBe('GET');
    req.flush({ count: 0, results: [] });
  });

  it('list(status) passes status as query param', () => {
    service.list('FAILED').subscribe();
    const req = controller.expectOne(`${BASE}/?status=FAILED`);
    expect(req.request.params.get('status')).toBe('FAILED');
    req.flush({ count: 0, results: [] });
  });

  it('getById() calls GET /api/v1/notifications/{id}/', () => {
    const id = 'abc-123';
    service.getById(id).subscribe();
    const req = controller.expectOne(`${BASE}/${id}/`);
    expect(req.request.method).toBe('GET');
    req.flush({});
  });

  it('send() calls POST /api/v1/notifications/send/ with payload', () => {
    const payload: SendNotificationPayload = {
      title: 'Test',
      message: 'Hello',
      channels: ['EMAIL'],
      recipients: [{ name: 'Fabio', email: 'fabio@example.com' }],
    };
    service.send(payload).subscribe();
    const req = controller.expectOne(`${BASE}/send/`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(payload);
    req.flush({});
  });

  it('retry() calls POST /api/v1/notifications/{id}/retry/', () => {
    const id = 'abc-123';
    service.retry(id).subscribe();
    const req = controller.expectOne(`${BASE}/${id}/retry/`);
    expect(req.request.method).toBe('POST');
    req.flush({ detail: 'queued' });
  });

  it('cancel() calls DELETE /api/v1/notifications/{id}/cancel/', () => {
    const id = 'abc-123';
    service.cancel(id).subscribe();
    const req = controller.expectOne(`${BASE}/${id}/cancel/`);
    expect(req.request.method).toBe('DELETE');
    req.flush(null);
  });
});
