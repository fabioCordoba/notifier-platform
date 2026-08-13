import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { Provider, ProviderPayload } from '../models/provider.model';

@Injectable({ providedIn: 'root' })
export class ProviderService {
  private http = inject(HttpClient);
  private base = `${environment.apiUrl}/api/v1/providers/`;

  list() {
    return this.http.get<Provider[]>(this.base);
  }

  create(data: ProviderPayload) {
    return this.http.post<Provider>(this.base, data);
  }

  update(id: string, data: ProviderPayload) {
    return this.http.put<Provider>(`${this.base}${id}/`, data);
  }

  remove(id: string) {
    return this.http.delete<void>(`${this.base}${id}/`);
  }
}
