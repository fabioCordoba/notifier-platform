import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { Template, CreateTemplatePayload } from '../models/template.model';
import { PaginatedResponse as PR } from '../models/notification.model';

@Injectable({ providedIn: 'root' })
export class TemplateService {
  private http = inject(HttpClient);
  private base = `${environment.apiUrl}/api/v1/templates`;

  list(): Observable<PR<Template>> {
    return this.http.get<PR<Template>>(`${this.base}/`);
  }

  getById(id: string): Observable<Template> {
    return this.http.get<Template>(`${this.base}/${id}/`);
  }

  create(payload: CreateTemplatePayload): Observable<Template> {
    return this.http.post<Template>(`${this.base}/`, payload);
  }

  update(id: string, payload: Partial<CreateTemplatePayload>): Observable<Template> {
    return this.http.put<Template>(`${this.base}/${id}/`, payload);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}/`);
  }
}
