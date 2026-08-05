import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Notification,
  SendNotificationPayload,
  PaginatedResponse,
} from '../models/notification.model';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private http = inject(HttpClient);
  private base = `${environment.apiUrl}/api/v1/notifications`;

  list(status?: string): Observable<PaginatedResponse<Notification>> {
    let params = new HttpParams();
    if (status) params = params.set('status', status);
    return this.http.get<PaginatedResponse<Notification>>(`${this.base}/`, { params });
  }

  getById(id: string): Observable<Notification> {
    return this.http.get<Notification>(`${this.base}/${id}/`);
  }

  send(payload: SendNotificationPayload): Observable<Notification> {
    return this.http.post<Notification>(`${this.base}/send/`, payload);
  }

  retry(id: string): Observable<{ detail: string }> {
    return this.http.post<{ detail: string }>(`${this.base}/${id}/retry/`, {});
  }

  cancel(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}/cancel/`);
  }
}
